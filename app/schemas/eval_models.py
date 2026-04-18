"""
LoveAdvisor V3 - Evaluation Models
Phase 1: Engineering Skeleton Initialization

This module contains Pydantic models for evaluation and testing.
These models are used for quality assessment, A/B testing, and system validation.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.schemas.request_models import AnalysisRequest
from app.schemas.result_models import AnalysisResult


class EvaluationType(str, Enum):
    """Types of evaluations."""
    QUALITY = "quality"
    SAFETY = "safety"
    UTILITY = "utility"
    PERFORMANCE = "performance"
    A_B_TEST = "a_b_test"
    USER_STUDY = "user_study"


class EvaluationStatus(str, Enum):
    """Evaluation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RatingScale(str, Enum):
    """Rating scales for evaluations."""
    ONE_TO_FIVE = "1-5"  # 1-5 stars
    ONE_TO_TEN = "1-10"  # 1-10 scale
    BINARY = "binary"  # Yes/No
    LIKERT = "likert"  # Strongly disagree to strongly agree (5-point)
    SEMANTIC_DIFFERENTIAL = "semantic_differential"  # Bipolar scales


class QualityMetric(BaseModel):
    """
    Model for quality evaluation metrics.
    """
    metric_name: str = Field(
        ...,
        description="Name of the quality metric",
        example="relevance"
    )
    score: float = Field(
        ...,
        description="Metric score (0.0-1.0 or scale-specific)",
        ge=0.0
    )
    scale: RatingScale = Field(
        RatingScale.ONE_TO_FIVE,
        description="Rating scale used for this metric"
    )
    weight: float = Field(
        1.0,
        description="Weight of this metric in overall quality score",
        ge=0.0,
        le=2.0
    )
    rationale: Optional[str] = Field(
        None,
        description="Rationale for the score"
    )
    evidence: Optional[List[str]] = Field(
        default_factory=list,
        description="Evidence supporting this score"
    )

    @validator('score')
    def validate_score_for_scale(cls, v, values):
        """Validate score based on rating scale."""
        scale = values.get('scale', RatingScale.ONE_TO_FIVE)

        if scale == RatingScale.ONE_TO_FIVE and not 1 <= v <= 5:
            raise ValueError('Score must be between 1 and 5 for 1-5 scale')
        elif scale == RatingScale.ONE_TO_TEN and not 1 <= v <= 10:
            raise ValueError('Score must be between 1 and 10 for 1-10 scale')
        elif scale == RatingScale.BINARY and v not in [0, 1]:
            raise ValueError('Score must be 0 or 1 for binary scale')
        elif scale == RatingScale.LIKERT and not 1 <= v <= 5:
            raise ValueError('Score must be between 1 and 5 for Likert scale')

        return v


class SafetyMetric(BaseModel):
    """
    Model for safety evaluation metrics.
    """
    safety_concern: str = Field(
        ...,
        description="Type of safety concern",
        example="harmful_advice"
    )
    detected: bool = Field(
        ...,
        description="Whether this safety concern was detected"
    )
    severity: Optional[str] = Field(
        None,
        description="Severity level if detected (low/medium/high/critical)"
    )
    confidence: float = Field(
        1.0,
        description="Confidence in detection (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    mitigation_applied: Optional[bool] = Field(
        None,
        description="Whether mitigation was applied"
    )
    evidence: Optional[List[str]] = Field(
        default_factory=list,
        description="Evidence supporting this safety assessment"
    )


class UtilityMetric(BaseModel):
    """
    Model for utility evaluation metrics.
    """
    aspect: str = Field(
        ...,
        description="Aspect of utility being measured",
        example="actionability"
    )
    score: float = Field(
        ...,
        description="Utility score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    user_rating: Optional[float] = Field(
        None,
        description="User rating for this aspect (if available)"
    )
    expert_rating: Optional[float] = Field(
        None,
        description="Expert rating for this aspect (if available)"
    )
    feedback: Optional[List[str]] = Field(
        default_factory=list,
        description="Feedback comments related to this aspect"
    )


class PerformanceMetric(BaseModel):
    """
    Model for performance evaluation metrics.
    """
    metric_name: str = Field(
        ...,
        description="Performance metric name",
        example="response_time"
    )
    value: float = Field(
        ...,
        description="Metric value"
    )
    unit: str = Field(
        ...,
        description="Unit of measurement",
        example="milliseconds"
    )
    target: Optional[float] = Field(
        None,
        description="Target value for this metric"
    )
    threshold: Optional[float] = Field(
        None,
        description="Threshold value (e.g., maximum acceptable)"
    )
    is_within_target: Optional[bool] = Field(
        None,
        description="Whether the value is within target range"
    )


class EvaluationRequest(BaseModel):
    """
    Request model for initiating an evaluation.
    """
    evaluation_type: EvaluationType = Field(
        ...,
        description="Type of evaluation to perform"
    )
    request: AnalysisRequest = Field(
        ...,
        description="Analysis request to evaluate"
    )
    result: Optional[AnalysisResult] = Field(
        None,
        description="Analysis result to evaluate (if already generated)"
    )
    reference_result: Optional[AnalysisResult] = Field(
        None,
        description="Reference result for comparison (e.g., expert analysis)"
    )
    evaluator_id: Optional[str] = Field(
        None,
        description="ID of the evaluator (human or automated)"
    )
    evaluation_criteria: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Criteria for this evaluation"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional evaluation metadata"
    )


class EvaluationResult(BaseModel):
    """
    Result of an evaluation.
    """
    evaluation_id: str = Field(
        ...,
        description="Unique evaluation ID"
    )
    evaluation_type: EvaluationType = Field(
        ...,
        description="Type of evaluation performed"
    )
    request_id: str = Field(
        ...,
        description="ID of the analyzed request"
    )
    status: EvaluationStatus = Field(
        EvaluationStatus.COMPLETED,
        description="Evaluation status"
    )

    # Metrics
    quality_metrics: Optional[List[QualityMetric]] = Field(
        default_factory=list,
        description="Quality evaluation metrics"
    )
    safety_metrics: Optional[List[SafetyMetric]] = Field(
        default_factory=list,
        description="Safety evaluation metrics"
    )
    utility_metrics: Optional[List[UtilityMetric]] = Field(
        default_factory=list,
        description="Utility evaluation metrics"
    )
    performance_metrics: Optional[List[PerformanceMetric]] = Field(
        default_factory=list,
        description="Performance metrics"
    )

    # Scores
    overall_quality_score: Optional[float] = Field(
        None,
        description="Overall quality score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    overall_safety_score: Optional[float] = Field(
        None,
        description="Overall safety score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    overall_utility_score: Optional[float] = Field(
        None,
        description="Overall utility score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    # Analysis
    strengths: Optional[List[str]] = Field(
        default_factory=list,
        description="Strengths identified in the evaluation"
    )
    weaknesses: Optional[List[str]] = Field(
        default_factory=list,
        description="Weaknesses or areas for improvement"
    )
    recommendations: Optional[List[str]] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )

    # Metadata
    evaluation_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the evaluation was performed"
    )
    evaluation_duration_ms: Optional[float] = Field(
        None,
        description="Duration of evaluation in milliseconds"
    )
    evaluator_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Information about the evaluator"
    )
    raw_evaluation_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Raw evaluation data for reference"
    )

    # Methods
    def calculate_overall_scores(self) -> Dict[str, float]:
        """
        Calculate overall scores from individual metrics.

        Returns:
            Dictionary of overall scores.
        """
        scores = {}

        # Calculate overall quality score
        if self.quality_metrics:
            weighted_sum = sum(m.score * m.weight for m in self.quality_metrics)
            total_weight = sum(m.weight for m in self.quality_metrics)
            if total_weight > 0:
                scores["overall_quality"] = weighted_sum / total_weight

        # Calculate overall safety score
        if self.safety_metrics:
            # Safety score is inverse of detected concerns
            total_concerns = len(self.safety_metrics)
            undetected_concerns = sum(1 for m in self.safety_metrics if not m.detected)
            if total_concerns > 0:
                scores["overall_safety"] = undetected_concerns / total_concerns

        # Calculate overall utility score
        if self.utility_metrics:
            avg_utility = sum(m.score for m in self.utility_metrics) / len(self.utility_metrics)
            scores["overall_utility"] = avg_utility

        return scores

    def get_failed_safety_checks(self) -> List[SafetyMetric]:
        """
        Get safety metrics where concerns were detected.

        Returns:
            List of safety metrics with detected concerns.
        """
        return [m for m in (self.safety_metrics or []) if m.detected]

    def get_low_quality_metrics(self, threshold: float = 0.6) -> List[QualityMetric]:
        """
        Get quality metrics below a threshold.

        Args:
            threshold: Quality threshold (default 0.6).

        Returns:
            List of quality metrics below threshold.
        """
        return [m for m in (self.quality_metrics or []) if m.score < threshold]

    def to_summary(self) -> Dict[str, Any]:
        """
        Create a summary of the evaluation.

        Returns:
            Evaluation summary dictionary.
        """
        scores = self.calculate_overall_scores()

        return {
            "evaluation_id": self.evaluation_id,
            "evaluation_type": self.evaluation_type,
            "status": self.status,
            "overall_scores": scores,
            "failed_safety_checks": len(self.get_failed_safety_checks()),
            "low_quality_metrics": len(self.get_low_quality_metrics()),
            "strengths_count": len(self.strengths or []),
            "weaknesses_count": len(self.weaknesses or []),
            "recommendations_count": len(self.recommendations or []),
            "evaluation_timestamp": self.evaluation_timestamp.isoformat(),
        }