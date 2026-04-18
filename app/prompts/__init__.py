"""
LoveAdvisor V3 - Prompts Package
Phase 1: Engineering Skeleton Initialization

This package contains prompt templates for different pipeline stages.
Prompts are organized by stage and version to enable A/B testing and gradual updates.

TODO: Import concrete prompt implementations as they are developed.
"""

from app.prompts.base_prompt import BasePrompt

__all__ = [
    "BasePrompt",
]