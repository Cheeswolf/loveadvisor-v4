"""
LoveAdvisor V3 - Signal Models
Phase 1: Engineering Skeleton Initialization

This module contains Pydantic models for emotional and relational signals.
These models represent the structured output of signal extraction.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator

from app.core.enums import SignalType


class EmotionalValence(str, Enum):
    """Emotional valence categories."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class EmotionalIntensity(str, Enum):
    """Emotional intensity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RelationshipStage(str, Enum):
    """Relationship stages."""
    DATING = "dating"
    COMMITTED = "committed"
    ENGAGED = "engaged"
    MARRIED = "married"
    SEPARATED = "separated"
    DIVORCED = "divorced"
    COMPLICATED = "complicated"
    UNKNOWN = "unknown"


class BaseSignal(BaseModel):
    """Base model for all signal types."""
    type: SignalType = Field(..., description="Type of signal")
    value: str = Field(..., description="Signal value")
    confidence: float = Field(
        ...,
        description="Confidence score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Text evidence supporting this signal"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional signal metadata"
    )

    @validator('confidence')
    def confidence_range(cls, v):
        """Ensure confidence is within valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return round(v, 3)


class EmotionalSignal(BaseSignal):
    """Model for emotional signals."""
    type: SignalType = Field(
        SignalType.EMOTIONAL_STATE,
        description="Type of emotional signal"
    )
    valence: Optional[EmotionalValence] = Field(
        None,
        description="Emotional valence (positive/negative/neutral/mixed)"
    )
    intensity: Optional[EmotionalIntensity] = Field(
        None,
        description="Emotional intensity level"
    )

    @validator('type')
    def valid_emotional_type(cls, v):
        """Validate that type is an emotional signal type."""
        emotional_types = [
            SignalType.EMOTIONAL_STATE,
            SignalType.EMOTIONAL_INTENSITY,
            SignalType.EMOTIONAL_VALENCE,
        ]
        if v not in emotional_types:
            raise ValueError(f"Type must be an emotional signal type: {emotional_types}")
        return v


class RelationalSignal(BaseSignal):
    """Model for relational signals."""
    type: SignalType = Field(
        SignalType.RELATIONSHIP_STAGE,
        description="Type of relational signal"
    )
    stage: Optional[RelationshipStage] = Field(
        None,
        description="Relationship stage if applicable"
    )
    quality_indicator: Optional[str] = Field(
        None,
        description="Indicator of relationship quality"
    )

    @validator('type')
    def valid_relational_type(cls, v):
        """Validate that type is a relational signal type."""
        relational_types = [
            SignalType.RELATIONSHIP_STAGE,
            SignalType.RELATIONSHIP_QUALITY,
            SignalType.COMMUNICATION_PATTERN,
            SignalType.CONFLICT_STYLE,
        ]
        if v not in relational_types:
            raise ValueError(f"Type must be a relational signal type: {relational_types}")
        return v


class BehavioralSignal(BaseSignal):
    """Model for behavioral signals."""
    type: SignalType = Field(
        SignalType.ATTACHMENT_STYLE,
        description="Type of behavioral signal"
    )
    pattern: Optional[str] = Field(
        None,
        description="Behavioral pattern identified"
    )
    consistency: Optional[float] = Field(
        None,
        description="Consistency of this behavioral pattern (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    @validator('type')
    def valid_behavioral_type(cls, v):
        """Validate that type is a behavioral signal type."""
        behavioral_types = [
            SignalType.ATTACHMENT_STYLE,
            SignalType.LOVE_LANGUAGE,
            SignalType.NEEDS_EXPRESSED,
        ]
        if v not in behavioral_types:
            raise ValueError(f"Type must be a behavioral signal type: {behavioral_types}")
        return v


class ContextualSignal(BaseSignal):
    """Model for contextual signals."""
    type: SignalType = Field(
        SignalType.CULTURAL_CONTEXT,
        description="Type of contextual signal"
    )
    influence_level: Optional[str] = Field(
        None,
        description="Level of contextual influence (high/medium/low)"
    )
    adaptation_needed: Optional[bool] = Field(
        None,
        description="Whether adaptation is needed for this context"
    )

    @validator('type')
    def valid_contextual_type(cls, v):
        """Validate that type is a contextual signal type."""
        contextual_types = [
            SignalType.CULTURAL_CONTEXT,
            SignalType.GENDER_DYNAMICS,
            SignalType.POWER_BALANCE,
        ]
        if v not in contextual_types:
            raise ValueError(f"Type must be a contextual signal type: {contextual_types}")
        return v


class SignalBundle(BaseModel):
    """
    Bundle of all signal types for a single analysis.

    This model organizes signals by category for easy access and processing.
    """
    emotional_signals: List[EmotionalSignal] = Field(
        default_factory=list,
        description="Emotional signals extracted"
    )
    relational_signals: List[RelationalSignal] = Field(
        default_factory=list,
        description="Relational signals extracted"
    )
    behavioral_signals: List[BehavioralSignal] = Field(
        default_factory=list,
        description="Behavioral signals extracted"
    )
    contextual_signals: List[ContextualSignal] = Field(
        default_factory=list,
        description="Contextual signals extracted"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Bundle metadata"
    )

    def get_signals_by_type(self, signal_type: SignalType) -> List[BaseSignal]:
        """
        Get all signals of a specific type.

        Args:
            signal_type: Type of signal to retrieve.

        Returns:
            List of signals matching the type.
        """
        all_signals = (
            self.emotional_signals +
            self.relational_signals +
            self.behavioral_signals +
            self.contextual_signals
        )
        return [signal for signal in all_signals if signal.type == signal_type]

    def get_confidence_summary(self) -> Dict[str, float]:
        """
        Get confidence summary by signal category.

        Returns:
            Dictionary mapping categories to average confidence.
        """
        categories = {
            "emotional": self.emotional_signals,
            "relational": self.relational_signals,
            "behavioral": self.behavioral_signals,
            "contextual": self.contextual_signals,
        }

        summary = {}
        for category, signals in categories.items():
            if signals:
                avg_confidence = sum(s.confidence for s in signals) / len(signals)
                summary[f"{category}_avg_confidence"] = round(avg_confidence, 3)
            else:
                summary[f"{category}_avg_confidence"] = 0.0

        return summary

    def to_flat_list(self) -> List[Dict[str, Any]]:
        """
        Convert signal bundle to flat list for storage or display.

        Returns:
            List of signal dictionaries.
        """
        flat_signals = []
        for category in ["emotional", "relational", "behavioral", "contextual"]:
            signals = getattr(self, f"{category}_signals")
            for signal in signals:
                flat_signal = signal.dict()
                flat_signal["category"] = category
                flat_signals.append(flat_signal)

        return flat_signals


# =============================================================================
# Phase 3: S2/S3 Localization Migration Models
# =============================================================================

class S2Signal(BaseModel):
    """
    Model for S2 signal extraction output.
    """
    initiative: str = Field(
        ...,
        description="谁在对话中更主动发起话题或推进对话？"
    )
    response_length: str = Field(
        ...,
        description="B的回应长度如何？"
    )
    emotional_tone: str = Field(
        ...,
        description="对话的情感温度是怎样的？"
    )
    topic_depth: str = Field(
        ...,
        description="对话涉及的话题深度如何？"
    )
    interaction_reciprocity: str = Field(
        ...,
        description="B如何承接A的话题？"
    )
    key_signals: List[str] = Field(
        default_factory=list,
        description="对话中出现的值得注意的具体信号"
    )

    @validator('initiative')
    def validate_initiative(cls, v):
        # Compatibility mapping for legacy values
        compatibility_map = {
            "A 更主动": "A更主动",
            "B 更主动": "B更主动",
        }
        # Apply mapping if exists
        v = compatibility_map.get(v, v)

        valid_values = {"A更主动", "B更主动", "双方接近", "无法判断"}
        if v not in valid_values:
            return "无法判断"
        return v

    @validator('response_length')
    def validate_response_length(cls, v):
        valid_values = {"短", "中", "长", "无法判断"}
        if v not in valid_values:
            return "无法判断"
        return v

    @validator('emotional_tone')
    def validate_emotional_tone(cls, v):
        valid_values = {"热", "温", "冷", "无法判断"}
        if v not in valid_values:
            return "无法判断"
        return v

    @validator('topic_depth')
    def validate_topic_depth(cls, v):
        valid_values = {"浅", "中", "深", "无法判断"}
        if v not in valid_values:
            return "无法判断"
        return v

    @validator('interaction_reciprocity')
    def validate_interaction_reciprocity(cls, v):
        valid_values = {"正向承接", "弱承接", "明显回避", "无法判断"}
        if v not in valid_values:
            return "无法判断"
        return v

    @validator('key_signals')
    def validate_key_signals(cls, v):
        if not isinstance(v, list):
            return []
        # Ensure all elements are strings
        return [str(item) for item in v]


class S3Signal(BaseModel):
    """
    Model for S3 signal summary output.
    """
    has_intimacy_signal: bool = Field(
        default=False,
        description="对话中是否有明确的亲密表达或暗示？"
    )
    has_relationship_probe: bool = Field(
        default=False,
        description="是否有对关系状态的试探或确认？"
    )
    has_positive_reciprocity: bool = Field(
        default=False,
        description="是否有明显的双向积极互动？"
    )
    has_rejection_signal: bool = Field(
        default=False,
        description="是否有明确的拒绝、回避或冷淡？"
    )
    has_push_pull_pattern: bool = Field(
        default=False,
        description="是否出现'推进-后退'的矛盾模式？"
    )
    has_sustained_coldness: bool = Field(
        default=False,
        description="是否出现持续性的冷淡或疏远？"
    )
    signal_summary: List[str] = Field(
        default_factory=list,
        description="用简短的语句总结识别到的主要信号"
    )

    @validator('signal_summary')
    def validate_signal_summary(cls, v):
        if not isinstance(v, list):
            return []
        # Ensure all elements are strings
        return [str(item) for item in v]