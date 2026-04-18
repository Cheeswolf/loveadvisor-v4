"""
LoveAdvisor V3 - Base LLM Provider
Phase 1: Engineering Skeleton Initialization

This module defines the base interface for LLM providers.
All concrete LLM providers must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    pass


class LLMQuotaExceededError(LLMError):
    """Raised when LLM quota is exceeded."""
    pass


class LLMContentFilterError(LLMError):
    """Raised when content is filtered by safety systems."""
    pass


@dataclass
class LLMRequest:
    """Request for LLM completion."""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    stop_sequences: Optional[List[str]] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for serialization."""
        return asdict(self)


@dataclass
class LLMResponse:
    """Response from LLM completion."""
    text: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    raw_response: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization."""
        result = asdict(self)
        # Convert datetime to ISO format string
        result['created_at'] = self.created_at.isoformat()
        return result


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    This class defines the interface that all LLM providers must implement.
    It enables swapping providers without changing pipeline code.

    All providers must support JSON generation for structured outputs.
    """

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Send a completion request to the LLM.

        Args:
            request: LLM request parameters.

        Returns:
            LLM response.

        Raises:
            LLMError: If the request fails.
            LLMTimeoutError: If the request times out.
            LLMQuotaExceededError: If quota is exceeded.
            LLMContentFilterError: If content is filtered.
        """
        pass

    @abstractmethod
    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        Send a chat completion request to the LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional provider-specific parameters.

        Returns:
            LLM response.

        Raises:
            LLMError: If the request fails.
        """
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate JSON-structured output from the LLM.

        This method enforces JSON output format, which is critical for
        LoveAdvisor's structured data pipeline. Providers must ensure
        the response is valid JSON that conforms to the optional schema.

        Args:
            prompt: The prompt text to send to the LLM.
            schema: Optional JSON schema describing expected output structure.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Parsed JSON dictionary from LLM response.

        Raises:
            LLMError: If the request fails.
            ValueError: If response cannot be parsed as JSON or violates schema.

        TODO: Implement JSON generation with schema validation and error handling.
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the model used by this provider.

        Returns:
            Model name string.

        TODO: Return actual model name from configuration.
        """
        pass

    @abstractmethod
    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming responses.

        Returns:
            True if streaming is supported, False otherwise.

        TODO: Implement based on provider capabilities.
        """
        pass

    @abstractmethod
    def supports_json_mode(self) -> bool:
        """
        Check if this provider has native JSON mode support.

        Native JSON mode ensures the LLM outputs valid JSON without
        additional parsing or formatting.

        Returns:
            True if native JSON mode is supported, False otherwise.

        TODO: Implement based on provider capabilities.
        """
        pass

    async def health_check(self) -> bool:
        """
        Perform a health check on the LLM provider.

        Returns:
            True if provider is healthy, False otherwise.

        TODO: Implement actual health check with test request.
        """
        # TODO: Implement proper health check
        return True

    def estimate_cost(self, request: LLMRequest) -> float:
        """
        Estimate the cost of a request.

        Args:
            request: LLM request parameters.

        Returns:
            Estimated cost in USD.
        """
        # Default implementation returns 0.0
        return 0.0