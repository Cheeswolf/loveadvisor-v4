"""
LoveAdvisor V4 - Analysis Record Models
Phase 3: User Behavior Tracking & Data Loop

This module contains Pydantic models for analysis records.
These models represent the combined request and result data for tracking
user behavior and enabling data feedback loops.

IMPORTANT: This is a schema-only design, no database dependency.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class AnalysisRecord(BaseModel):
    """
    Core data structure for tracking analysis requests and results.

    This model combines the original request data with the analysis results,
    enabling comprehensive tracking of user interactions for future
    data feedback loops and behavioral analysis.

    Schema-only design: no database persistence logic included.
    """
    # Request fields from AnalysisRequest
    request_id: str = Field(..., description="Unique identifier for this analysis request")
    chat_text: str = Field(..., description="The original conversation text analyzed")
    user_question: str = Field(..., description="User's question or concern about the relationship")
    provider_name: str = Field(..., description="LLM provider name used for analysis")

    # Result fields from AnalysisResult
    relationship_stage: str = Field(
        ...,
        description="Relationship stage: 初识期 / 暧昧期 / 拉扯期 / 冷淡期 / 无法判断"
    )
    interest_level: str = Field(
        ...,
        description="Interest level: 低 / 中 / 高 / 无法判断"
    )
    suggestions: List[str] = Field(
        ...,
        description="Actionable suggestions for the user"
    )
    next_step: str = Field(
        ...,
        description="Clear next step recommendation"
    )

    # Metadata fields
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when this record was created"
    )

    # Optional additional result fields for completeness
    psychological_analysis: Optional[str] = Field(
        None,
        description="Psychological analysis based on signals"
    )
    risk_points: Optional[List[str]] = Field(
        None,
        description="Identified risk points in the relationship"
    )
    debug: Optional[Dict[str, Any]] = Field(
        None,
        description="Debug information if debug mode was enabled"
    )

    # Validators
    @validator('relationship_stage')
    def validate_relationship_stage(cls, v):
        """Validate relationship stage values."""
        valid_values = {"初识期", "暧昧期", "拉扯期", "冷淡期", "无法判断"}
        if v not in valid_values:
            return "无法判断"
        return v

    @validator('interest_level')
    def validate_interest_level(cls, v):
        """Validate interest level values."""
        valid_values = {"低", "中", "高", "无法判断"}
        if v not in valid_values:
            return "无法判断"
        return v

    @validator('suggestions')
    def ensure_min_suggestions(cls, v):
        """Ensure at least two suggestions."""
        if len(v) < 2:
            return v + ["保持适度互动频率"] if v else ["保持观察", "避免重大决定"]
        return v

    @validator('suggestions', 'risk_points')
    def truncate_list_items(cls, v):
        """Truncate individual list items if too long."""
        if v is None:
            return v
        return [item[:100] + "..." if len(item) > 100 else item for item in v]

    @validator('next_step')
    def truncate_next_step(cls, v):
        """Truncate next step if too long."""
        if len(v) > 100:
            return v[:97] + "..."
        return v

    @validator('psychological_analysis')
    def truncate_psychological_analysis(cls, v):
        """Truncate psychological analysis if too long."""
        if v and len(v) > 300:
            return v[:297] + "..."
        return v

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "request_id": "req_123456",
                "chat_text": "她今天回复消息很慢，不知道是不是对我没兴趣了",
                "user_question": "她是不是不喜欢我了？",
                "provider_name": "deepseek",
                "relationship_stage": "暧昧期",
                "interest_level": "中",
                "suggestions": ["保持适度互动频率", "观察后续回应"],
                "next_step": "继续观察互动模式",
                "created_at": "2024-01-15T10:30:00",
                "psychological_analysis": "对方可能处于观望状态，需要更多信号判断",
                "risk_points": ["回复速度变慢可能表示兴趣下降"],
                "debug": None
            }
        }

    @classmethod
    def from_request_and_result(cls, request, result, request_id: Optional[str] = None):
        """
        Create an AnalysisRecord from an AnalysisRequest and AnalysisResult.

        Args:
            request: AnalysisRequest instance
            result: AnalysisResult instance
            request_id: Optional request ID (uses request.request_id if available)

        Returns:
            AnalysisRecord instance
        """
        # Use provided request_id, fall back to request.request_id, generate if needed
        final_request_id = request_id or request.request_id or f"req_{int(datetime.now().timestamp())}"

        return cls(
            request_id=final_request_id,
            chat_text=request.chat_text,
            user_question=request.user_question,
            provider_name=request.provider_name,
            relationship_stage=result.relationship_stage,
            interest_level=result.interest_level,
            suggestions=result.suggestions,
            next_step=result.next_step,
            psychological_analysis=result.psychological_analysis,
            risk_points=result.risk_points,
            debug=result.debug
        )


# Alias for backward compatibility
AnalyzeRecord = AnalysisRecord