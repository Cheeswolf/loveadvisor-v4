"""
LoveAdvisor V3 - Base Utilities
Phase 1: Engineering Skeleton Initialization

This module defines the base class for utility functions.
All utility modules should follow this structure for consistency.

TODO: Implement concrete utilities for text processing, logging, retries, etc.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseUtility(ABC):
    """
    Abstract base class for utility modules.

    This class defines the interface that utility modules should follow.
    It ensures consistent error handling and configuration across utilities.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize utility with configuration.

        Args:
            config: Configuration dictionary for the utility.
        """
        self.config = config or {}

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the utility (e.g., setup connections, load resources).

        Raises:
            InitializationError: If initialization fails.
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up resources used by the utility.
        """
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """
        Check if the utility is functioning correctly.

        Returns:
            True if healthy, False otherwise.
        """
        pass

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the utility's configuration.

        Returns:
            Configuration summary dictionary.
        """
        return {
            "utility_type": self.__class__.__name__,
            "config": self.config
        }