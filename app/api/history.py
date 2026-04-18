"""
LoveAdvisor V4 - History API Endpoint
Phase 4: Historical Records Page Minimal Implementation

This module provides an API endpoint for retrieving analysis history records.
"""

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.analysis_record_store import AnalysisRecordStore
from app.schemas.analysis_record_models import AnalysisRecord

router = APIRouter()


class HistoryRecordResponse(BaseModel):
    """Simplified history record for API response."""
    request_id: str = Field(..., description="Unique identifier for this analysis request")
    relationship_stage: str = Field(..., description="Relationship stage: 初识期 / 暧昧期 / 拉扯期 / 冷淡期 / 无法判断")
    interest_level: str = Field(..., description="Interest level: 低 / 中 / 高 / 无法判断")
    next_step: str = Field(..., description="Clear next step recommendation")
    created_at: str = Field(..., description="Timestamp when this record was created (ISO format)")
    user_question: Optional[str] = Field(None, description="User's original question")
    provider_name: Optional[str] = Field(None, description="LLM provider name used for analysis")

    @classmethod
    def from_analysis_record(cls, record: AnalysisRecord) -> "HistoryRecordResponse":
        """Convert an AnalysisRecord to a HistoryRecordResponse."""
        return cls(
            request_id=record.request_id,
            relationship_stage=record.relationship_stage,
            interest_level=record.interest_level,
            next_step=record.next_step,
            created_at=record.created_at.isoformat() if hasattr(record.created_at, 'isoformat') else str(record.created_at),
            user_question=record.user_question,
            provider_name=record.provider_name
        )


class HistoryResponse(BaseModel):
    """Response model for the history endpoint."""
    count: int = Field(..., description="Number of records returned")
    records: List[HistoryRecordResponse] = Field(..., description="List of history records")
    limit: int = Field(default=20, description="Maximum number of records requested")


@router.get("/history", response_model=HistoryResponse)
async def get_history(limit: int = 20) -> HistoryResponse:
    """
    Retrieve analysis history records.

    This endpoint returns the most recent analysis records stored in the system.
    Records are returned in reverse chronological order (newest first).

    Args:
        limit: Maximum number of records to return (default 20, max 100)

    Returns:
        HistoryResponse containing the requested number of records.
    """
    # Validate limit parameter
    if limit <= 0:
        limit = 20
    if limit > 100:
        limit = 100

    # Read records from store
    records = AnalysisRecordStore.read_latest_records(limit=limit)

    # Convert to response format (reverse to show newest first)
    history_records = [HistoryRecordResponse.from_analysis_record(record) for record in reversed(records)]

    return HistoryResponse(
        count=len(history_records),
        records=history_records,
        limit=limit
    )


@router.get("/history/{request_id}", response_model=AnalysisRecord)
async def get_history_record(request_id: str) -> AnalysisRecord:
    """
    Retrieve a specific analysis record by its request_id.

    This endpoint returns the full analysis record including all fields.

    Args:
        request_id: The unique identifier of the analysis request

    Returns:
        AnalysisRecord containing all data for this analysis.

    Raises:
        HTTPException 404 if record not found
    """
    # Read all records and find matching request_id
    records = AnalysisRecordStore.read_latest_records(limit=1000)  # Read enough to find record
    for record in records:
        if record.request_id == request_id:
            return record

    # If not found, raise 404
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"History record with request_id '{request_id}' not found")