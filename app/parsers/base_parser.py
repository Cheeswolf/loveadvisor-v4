"""
LoveAdvisor V3 - Base Parser
Phase 1: Engineering Skeleton Initialization

This module defines the base interface for response parsers.
All parsers should follow this structure for consistency.

TODO: Implement concrete parsers for each pipeline stage output.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class ParseError(Exception):
    """Base exception for parsing errors."""
    pass


class ValidationError(Exception):
    """Raised when parsed data fails validation."""
    pass


class BaseParser(ABC):
    """
    Abstract base class for all response parsers.

    This class defines the interface that all parsers must implement.
    It ensures consistent parsing and validation across pipeline stages.
    """

    @abstractmethod
    async def parse(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse raw LLM response into structured data.

        Args:
            raw_response: Raw text response from LLM.

        Returns:
            Structured dictionary representation of the parsed data.

        Raises:
            ParseError: If parsing fails due to malformed response.
        """
        pass

    @abstractmethod
    async def validate(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Validate parsed data against schema.

        Args:
            parsed_data: Parsed data dictionary.

        Returns:
            True if data passes validation, False otherwise.

        Raises:
            ValidationError: If validation fails with detailed error messages.
        """
        pass

    @abstractmethod
    def get_expected_schema(self) -> Dict[str, Any]:
        """
        Get the expected schema for parsed data.

        Returns:
            Dictionary describing the expected structure and types.
        """
        pass

    async def parse_and_validate(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse and validate response in one operation.

        Args:
            raw_response: Raw text response from LLM.

        Returns:
            Validated parsed data.

        Raises:
            ParseError: If parsing fails.
            ValidationError: If validation fails.
        """
        parsed = await self.parse(raw_response)
        is_valid = await self.validate(parsed)
        if not is_valid:
            raise ValidationError("Parsed data failed validation")
        return parsed