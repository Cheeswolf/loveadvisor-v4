"""
LoveAdvisor V3 - LLM Package
Phase 1: Engineering Skeleton Initialization

This package contains abstractions and implementations for LLM providers.
It enables the system to work with multiple LLM providers (DeepSeek, OpenAI, etc.)
through a unified interface, with easy switching and mocking for testing.
"""

from app.llm.base_provider import BaseLLMProvider, LLMResponse, LLMRequest
from app.llm.provider_factory import LLMProviderFactory, get_provider
from app.llm.deepseek_provider import DeepSeekProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.mock_provider import MockProvider

__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "LLMRequest",
    "LLMProviderFactory",
    "get_provider",
    "DeepSeekProvider",
    "OpenAIProvider",
    "MockProvider",
]