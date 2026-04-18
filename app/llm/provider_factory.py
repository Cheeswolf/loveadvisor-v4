"""
LoveAdvisor V3 - LLM Provider Factory
Phase 1: Engineering Skeleton Initialization

This module provides a factory for creating LLM provider instances.
It manages provider configuration, initialization, and lifecycle.
"""

import importlib
import os
from typing import Dict, Any, Optional, Type, List
from app.llm.base_provider import BaseLLMProvider
from app.core.enums import LLMProvider as LLMProviderEnum
from configs import settings


class LLMProviderFactory:
    """
    Factory for creating and managing LLM provider instances.

    This factory handles:
    1. Provider registration and discovery
    2. Configuration loading and validation
    3. Instance caching and reuse
    4. Fallback provider selection
    """

    # Registry of provider classes
    _providers: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """
        Register a provider class.

        Args:
            name: Provider name (e.g., "deepseek", "openai", "mock").
            provider_class: Provider class implementing BaseLLMProvider.
        """
        cls._providers[name.lower()] = provider_class

    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create a provider instance.

        Args:
            provider_name: Name of the provider to create.
            config: Provider-specific configuration.
            **kwargs: Additional initialization parameters.

        Returns:
            Provider instance.

        Raises:
            ValueError: If provider is not registered or cannot be created.
        """
        provider_name = provider_name.lower()
        config = config or {}

        # Check if provider is registered
        if provider_name not in cls._providers:
            raise ValueError(f"Provider '{provider_name}' is not registered")

        try:
            # Create provider instance
            provider_class = cls._providers[provider_name]
            instance = provider_class(config, **kwargs)
            return instance
        except Exception as e:
            raise ValueError(f"Failed to create provider '{provider_name}': {str(e)}")

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available provider names.

        Returns:
            List of registered provider names.
        """
        return list(cls._providers.keys())

    @classmethod
    def get_default_provider(cls) -> str:
        """
        Get the default provider name.

        Returns:
            Default provider name.
        """
        # Read from configuration
        return settings.LLM_PROVIDER


# Global factory instance
_factory = LLMProviderFactory()


def _get_provider_default_config(provider_name: str) -> Dict[str, Any]:
    """
    Get default configuration for a provider from settings.

    Args:
        provider_name: Provider name.

    Returns:
        Default configuration dictionary.
    """
    provider_name_lower = provider_name.lower()

    # Set default model based on provider
    if provider_name_lower == "deepseek":
        default_model = "deepseek-chat"
    elif provider_name_lower == "openai":
        default_model = "gpt-3.5-turbo"
    elif provider_name_lower == "mock":
        default_model = "mock-model-1.0"
    else:
        default_model = settings.LLM_DEFAULT_MODEL

    config = {
        "model": default_model,
        "temperature": settings.LLM_DEFAULT_TEMPERATURE,
        "max_tokens": settings.LLM_MAX_TOKENS,
    }

    # Add API key based on provider
    if provider_name_lower == "deepseek":
        config["api_key"] = settings.DEEPSEEK_API_KEY
    elif provider_name_lower == "openai":
        config["api_key"] = settings.OPENAI_API_KEY
    elif provider_name_lower == "anthropic":
        config["api_key"] = settings.ANTHROPIC_API_KEY

    return config


def get_provider(
    provider_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> BaseLLMProvider:
    """
    Convenience function to get a provider instance.

    Args:
        provider_name: Optional provider name. Uses default if not specified.
        config: Provider configuration.
        **kwargs: Additional initialization parameters.

    Returns:
        Provider instance.
    """
    if provider_name is None:
        provider_name = _factory.get_default_provider()

    # Merge default config with provided config
    default_config = _get_provider_default_config(provider_name)
    if config:
        default_config.update(config)

    return _factory.create_provider(provider_name, default_config, **kwargs)


def register_providers() -> None:
    """
    Register all built-in providers.

    This function should be called during application initialization.
    """
    # Import provider classes to avoid circular imports
    from app.llm.deepseek_provider import DeepSeekProvider
    from app.llm.openai_provider import OpenAIProvider
    from app.llm.mock_provider import MockProvider

    # Register providers
    _factory.register_provider("deepseek", DeepSeekProvider)
    _factory.register_provider("openai", OpenAIProvider)
    _factory.register_provider("mock", MockProvider)


# Auto-register providers when module is imported
try:
    register_providers()
except ImportError:
    # Providers may not be fully implemented yet during skeleton phase
    pass