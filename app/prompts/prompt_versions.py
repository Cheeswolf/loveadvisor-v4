"""
LoveAdvisor V3 - Prompt Version Management
Phase 1: Engineering Skeleton Initialization

This module manages different versions of prompts for A/B testing and gradual updates.
It provides functions to retrieve specific prompt versions based on configuration.
"""

from typing import Dict, Any, Optional, List
from enum import Enum


class PromptStage(Enum):
    """Pipeline stages that use prompts."""
    PREPROCESS = "preprocess"
    S2 = "s2"
    S3 = "s3"
    S5 = "s5"


class PromptVersion(Enum):
    """Available prompt versions."""
    V1 = "v1"  # Original version
    V2 = "v2"  # Improved version
    CONCISE = "concise"  # Shorter version
    DETAILED = "detailed"  # More detailed version
    TEST = "test"  # Experimental version


# Prompt registry mapping (stage -> version -> prompt)
_PROMPT_REGISTRY: Dict[str, Dict[str, str]] = {
    "preprocess": {
        "v1": """
Clean and prepare this relationship advice query: {user_input}
Context: {user_context}
Provide cleaned text and basic context enrichment.
""",
        "concise": """
Clean and prepare: {user_input}
Context: {user_context}
Provide cleaned text.
""",
    },
    "s2": {
        "v1": """
Extract relationship signals from: {cleaned_text}
Context: {enriched_context}
Provide emotional and relational signals.
""",
        "detailed": """
Comprehensively analyze relationship signals in: {cleaned_text}
Context: {enriched_context}
Extract emotional, relational, behavioral, and contextual signals with confidence scores.
""",
    },
    "s3": {
        "v1": """
Summarize signals: {signals_json}
Provide main themes and underlying needs.
""",
        "detailed": """
Synthesize and summarize: {signals_json}
Provide themes, needs, dynamics, urgency assessment, and cultural considerations.
""",
    },
    "s5": {
        "v1": """
Generate advice for: {signal_summary_json}
Provide practical strategies.
""",
        "detailed": """
Generate comprehensive strategies: {signal_summary_json}
Include psychological analysis, primary/secondary strategies, safety recommendations, risk points, and monitoring suggestions.
""",
    },
}


def get_prompt(
    stage: PromptStage,
    version: PromptVersion = PromptVersion.V1,
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Get a prompt for a specific stage and version.

    Args:
        stage: Pipeline stage.
        version: Prompt version.
        params: Parameters to format into the prompt.

    Returns:
        Formatted prompt string.

    Raises:
        KeyError: If stage or version not found.
    """
    stage_key = stage.value
    version_key = version.value

    if stage_key not in _PROMPT_REGISTRY:
        raise KeyError(f"Stage '{stage_key}' not found in prompt registry")

    if version_key not in _PROMPT_REGISTRY[stage_key]:
        raise KeyError(f"Version '{version_key}' not found for stage '{stage_key}'")

    prompt_template = _PROMPT_REGISTRY[stage_key][version_key]

    if params:
        try:
            return prompt_template.format(**params)
        except KeyError as e:
            raise ValueError(f"Missing parameter for prompt formatting: {e}")

    return prompt_template


def get_prompt_version(
    stage: str,
    version: str = "v1",
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to get prompt version.

    Args:
        stage: Stage name as string.
        version: Version string.
        params: Formatting parameters.

    Returns:
        Formatted prompt.
    """
    try:
        stage_enum = PromptStage(stage)
        version_enum = PromptVersion(version)
        return get_prompt(stage_enum, version_enum, params)
    except ValueError:
        # Fallback to direct registry access
        if stage in _PROMPT_REGISTRY and version in _PROMPT_REGISTRY[stage]:
            prompt = _PROMPT_REGISTRY[stage][version]
            if params:
                return prompt.format(**params)
            return prompt
        else:
            raise KeyError(f"Prompt not found: stage={stage}, version={version}")


def list_available_versions(stage: Optional[str] = None) -> Dict[str, List[str]]:
    """
    List available prompt versions.

    Args:
        stage: Optional stage name to filter.

    Returns:
        Dictionary mapping stages to available versions.
    """
    if stage:
        if stage not in _PROMPT_REGISTRY:
            return {stage: []}
        return {stage: list(_PROMPT_REGISTRY[stage].keys())}

    return {stage: list(versions.keys()) for stage, versions in _PROMPT_REGISTRY.items()}


def register_prompt(
    stage: str,
    version: str,
    prompt_template: str,
    overwrite: bool = False
) -> None:
    """
    Register a new prompt or update an existing one.

    Args:
        stage: Stage name.
        version: Version name.
        prompt_template: Prompt template string.
        overwrite: Whether to overwrite existing prompt.

    Raises:
        ValueError: If prompt exists and overwrite is False.
    """
    if stage not in _PROMPT_REGISTRY:
        _PROMPT_REGISTRY[stage] = {}

    if version in _PROMPT_REGISTRY[stage] and not overwrite:
        raise ValueError(f"Prompt version '{version}' already exists for stage '{stage}'")

    _PROMPT_REGISTRY[stage][version] = prompt_template


def get_all_prompts() -> Dict[str, Dict[str, str]]:
    """
    Get all registered prompts.

    Returns:
        Complete prompt registry.
    """
    return _PROMPT_REGISTRY.copy()