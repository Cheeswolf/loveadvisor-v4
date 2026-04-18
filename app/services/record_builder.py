"""
LoveAdvisor V4 - Analysis Record Builder Service
Phase 3: User Behavior Tracking & Data Loop

This module provides minimal logic for building AnalysisRecord objects
from analysis requests and results, without any persistence.

This service is designed to be integrated into the existing analyze endpoint
to enable record building for future data feedback loops, without modifying
the existing API response structure or adding database dependencies.
"""

from typing import Optional
from app.schemas.request_models import AnalysisRequest
from app.schemas.result_models import AnalysisResult
from app.schemas.analysis_record_models import AnalysisRecord


class RecordBuilder:
    """
    Minimal service for building AnalysisRecord objects.

    This class encapsulates the logic for creating analysis records from
    request and result objects, reusing the existing from_request_and_result
    factory method.
    """

    @staticmethod
    def build_record(
        request: AnalysisRequest,
        result: AnalysisResult,
        request_id: Optional[str] = None
    ) -> AnalysisRecord:
        """
        Build an AnalysisRecord from request and result objects.

        This method delegates to AnalysisRecord.from_request_and_result()
        to ensure consistency and avoid duplicate mapping logic.

        Args:
            request: AnalysisRequest instance
            result: AnalysisResult instance
            request_id: Optional request ID override

        Returns:
            AnalysisRecord instance (not persisted)
        """
        return AnalysisRecord.from_request_and_result(
            request=request,
            result=result,
            request_id=request_id
        )


# Convenience function for direct usage
def build_analysis_record(
    request: AnalysisRequest,
    result: AnalysisResult,
    request_id: Optional[str] = None
) -> AnalysisRecord:
    """
    Convenience function for building analysis records.

    This is a thin wrapper around RecordBuilder.build_record() for
    simpler import and usage in API endpoints.

    Args:
        request: AnalysisRequest instance
        result: AnalysisResult instance
        request_id: Optional request ID override

    Returns:
        AnalysisRecord instance (not persisted)
    """
    return RecordBuilder.build_record(request, result, request_id)