"""
LoveAdvisor V3 - Core Package
Phase 1: Engineering Skeleton Initialization

This package contains core orchestration and runtime management components:
- PipelineOrchestrator: Coordinates the execution of pipeline stages
- RuntimeContext: Maintains request-specific state and configuration
- Enums: Shared enumeration types for pipeline stages, signal types, etc.
"""

from app.core.runtime_context import RuntimeContext
from app.core.enums import PipelineStage, SignalType, StrategyType, OutputFormat

__all__ = [
    "RuntimeContext",
    "PipelineStage",
    "SignalType",
    "StrategyType",
    "OutputFormat",
]