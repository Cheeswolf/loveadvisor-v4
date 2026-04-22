"""
LoveAdvisor V3 - Request Models
Phase 1: Engineering Skeleton Initialization

This module contains Pydantic models for API requests.
These models validate and document the expected request formats.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """
    Request model for the main analysis endpoint.

    This model captures all information needed for a complete analysis,
    including user input, context, and configuration overrides.
    """
    chat_text: str = Field(..., description="The conversation text to analyze")
    user_question: str = Field(..., description="User's question or concern about the relationship")
    provider_name: str = Field("deepseek", description="LLM provider name: 'mock' or 'deepseek'")
    debug: bool = Field(False, description="Enable debug mode to include intermediate results")

    # Optional fields for backward compatibility
    request_id: Optional[str] = Field(None, description="Unique identifier for this analysis request")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional user context")
    config_overrides: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuration overrides")


# Alias for backward compatibility
AnalyzeRequest = AnalysisRequest


class DebugRequest(BaseModel):
    """
    Request model for debug and testing endpoints.

    This model allows developers to test specific pipeline stages
    with controlled inputs and configuration.
    """
    conversation_text: str = Field(..., description="Conversation text for debugging")
    provider_name: str = Field("mock", description="LLM provider to use")
    stage: Optional[str] = Field(None, description="Specific pipeline stage to test")


class HealthCheckRequest(BaseModel):
    """
    Request model for health check endpoints.

    This model supports detailed health check requests with
    component-specific testing options.
    """
    component: Optional[str] = Field(None, description="Specific component to test")
    detailed: bool = Field(False, description="Run detailed health checks")