"""
LoveAdvisor V3 - Runtime Context
Phase 1: Engineering Skeleton Initialization

This module defines the RuntimeContext class, which maintains request-specific
state throughout the pipeline execution. It serves as a central data structure
for passing information between pipeline stages and services.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from app.core.enums import PipelineStage


@dataclass
class RuntimeContext:
    """
    Runtime context for a single analysis request.

    This class encapsulates all request-specific data, configuration, and state
    that flows through the pipeline. It is immutable from the perspective of
    pipeline stages (except via designated setters) to ensure data integrity.

    Attributes:
        request_id: Unique identifier for this request
        user_input: Raw user input text
        user_context: Optional user-provided context (demographics, history, etc.)
        config_overrides: Request-specific configuration overrides
        created_at: Timestamp when the context was created
        current_stage: Current pipeline stage being executed
        stage_outputs: Outputs from each completed pipeline stage
        processing_start_time: When pipeline execution began
        processing_time_ms: Total processing time in milliseconds
        error: Error message if pipeline failed
        metadata: Arbitrary metadata for extensibility
    """
    request_id: str
    user_input: str
    user_context: Dict[str, Any] = field(default_factory=dict)
    config_overrides: Dict[str, Any] = field(default_factory=dict)

    # Internal state
    created_at: datetime = field(default_factory=datetime.utcnow)
    current_stage: Optional[PipelineStage] = None
    stage_outputs: Dict[PipelineStage, Any] = field(default_factory=dict)
    processing_start_time: Optional[float] = None
    processing_time_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize derived fields."""
        if not self.request_id:
            self.request_id = self._generate_request_id()

    @staticmethod
    def _generate_request_id() -> str:
        """Generate a unique request ID."""
        return f"req_{uuid.uuid4().hex[:16]}_{int(time.time())}"

    def set_current_stage(self, stage: PipelineStage) -> None:
        """Set the current pipeline stage."""
        self.current_stage = stage
        if self.processing_start_time is None:
            self.processing_start_time = time.time()

    def set_stage_output(self, stage: PipelineStage, output: Any) -> None:
        """Store the output of a pipeline stage."""
        self.stage_outputs[stage] = output

    def get_stage_output(self, stage: PipelineStage) -> Optional[Any]:
        """Retrieve the output of a pipeline stage."""
        return self.stage_outputs.get(stage)

    def set_processing_time(self, processing_time_seconds: float) -> None:
        """Set the total processing time."""
        self.processing_time_ms = processing_time_seconds * 1000

    def get_processing_time(self) -> Optional[float]:
        """Get the processing time in milliseconds."""
        return self.processing_time_ms

    def set_error(self, error_message: str) -> None:
        """Set an error message."""
        self.error = error_message

    def get_error(self) -> Optional[str]:
        """Get the error message."""
        return self.error

    def is_success(self) -> bool:
        """Check if the pipeline succeeded (no error)."""
        return self.error is None

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging or serialization."""
        return {
            "request_id": self.request_id,
            "user_input": self.user_input,
            "user_context": self.user_context,
            "config_overrides": self.config_overrides,
            "created_at": self.created_at.isoformat(),
            "current_stage": self.current_stage.value if self.current_stage else None,
            "stage_outputs": {
                stage.value: output for stage, output in self.stage_outputs.items()
            },
            "processing_time_ms": self.processing_time_ms,
            "error": self.error,
            "metadata": self.metadata,
        }

    def get_model_used(self) -> str:
        """Get the LLM model used for this request (from config or metadata)."""
        # TODO: Read from actual configuration
        return self.config_overrides.get("model", "mock")


class ContextManager:
    """
    Manages creation and retrieval of runtime contexts.

    This class provides a factory for creating contexts and can be extended
    to support context pooling, caching, or distributed context tracking.
    """

    @staticmethod
    def create_context(
        user_input: str,
        user_context: Optional[Dict[str, Any]] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> RuntimeContext:
        """
        Create a new runtime context.

        Args:
            user_input: Raw user input text
            user_context: Optional user-provided context
            config_overrides: Request-specific configuration overrides
            request_id: Optional custom request ID

        Returns:
            New RuntimeContext instance.
        """
        return RuntimeContext(
            request_id=request_id or RuntimeContext._generate_request_id(),
            user_input=user_input,
            user_context=user_context or {},
            config_overrides=config_overrides or {},
        )