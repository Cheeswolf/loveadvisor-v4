"""
LoveAdvisor V3 - Analysis API Endpoint
Phase 1: Engineering Skeleton Initialization

This module defines the main analysis endpoint that orchestrates the full pipeline.
"""

import uuid
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.request_models import AnalysisRequest
from app.schemas.result_models import AnalyzeResult
from app.core.pipeline_orchestrator import run_analysis_async
from app.services.analysis_record_store import AnalysisRecordStore


router = APIRouter()


class AnalysisResponse(BaseModel):
    """Response model for the analysis endpoint."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this analysis request")
    status: str = Field("success", description="Processing status: 'success' or 'error'")
    result: AnalyzeResult = Field(..., description="Analysis results")
    error_message: str = Field("", description="Error message if status is 'error'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """
    Main analysis endpoint that processes user input through the V3 pipeline.

    Pipeline stages:
    1. S2 signal extraction
    2. S3 signal summary
    3. R1 rule inference
    4. S5 strategy generation
    5. Guardrail application

    Args:
        request: Analysis request containing chat text, user question, provider, and debug flag.

    Returns:
        AnalysisResponse with results or error details.
    """
    try:
        # 入口日志：记录请求信息
        import logging
        import datetime
        logger = logging.getLogger(__name__)
        logger.info(f"[ANALYZE REQUEST] time={datetime.datetime.now().isoformat()}, chat_text_len={len(request.chat_text)}, provider={request.provider_name}, debug={request.debug}")
        logger.info(f"[ANALYZE REQUEST] chat_text_preview={request.chat_text[:200]}")
        # 调试：打印接收到的 provider_name
        print(f"[后端-analyze] 接收到的 provider_name: {request.provider_name}")
        # Generate request ID if not provided
        request_id = request.request_id or str(uuid.uuid4())

        # Run the analysis pipeline
        result_dict = await run_analysis_async(
            chat_text=request.chat_text,
            user_question=request.user_question,
            provider_name=request.provider_name,
            debug=request.debug
        )

        # Convert to AnalyzeResult model
        result_model = AnalyzeResult(**result_dict)

        # 返回前日志：记录分析结果
        logger.info(f"[ANALYZE RESULT] relationship_stage={result_model.relationship_stage}, interest_level={result_model.interest_level}, degraded=False")

        # 成功路径记录接入：构建并保存分析记录
        try:
            AnalysisRecordStore.save_record_from_request_and_result(
                request=request,
                result=result_model,
                request_id=request_id
            )
            logger.info(f"[ANALYZE RECORD] Record saved successfully for request_id={request_id}")
        except Exception as e:
            # 最小异常保护：记录错误但不影响正常响应
            logger.error(f"[ANALYZE RECORD] Failed to save record for request_id={request_id}: {e}", exc_info=True)

        # Build response
        # 调试：打印最终使用的 provider
        print(f"[后端-analyze] metadata.provider_used: {request.provider_name}")
        return AnalysisResponse(
            request_id=request_id,
            status="success",
            result=result_model,
            metadata={
                "pipeline_version": "v3",
                "provider_used": request.provider_name,
                "debug_mode": request.debug,
            }
        )

    except Exception as e:
        # Return error response instead of raising HTTPException to maintain consistent response format
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Analysis pipeline failed: {e}", exc_info=True)

        # Prepare debug info if debug mode is enabled
        debug_info = None
        if request.debug:
            tb_summary = traceback.format_exc()
            if len(tb_summary) > 500:
                tb_summary = tb_summary[:497] + "..."
            debug_info = {
                "raw_chat_text": request.chat_text,
                "provider_name": request.provider_name,
                "pipeline_error_stage": "API_ERROR",
                "pipeline_error_message": str(e),
                "traceback_summary": tb_summary,
            }

        # Create error result with optional debug field
        error_result_kwargs = {
            "relationship_stage": "无法判断",
            "interest_level": "无法判断",
            "psychological_analysis": "分析过程中出现错误，请稍后重试。",
            "risk_points": ["系统处理异常"],
            "suggestions": ["保持现状观察", "避免重大决定"],
            "next_step": "系统错误，建议暂停使用或联系支持",
        }
        if debug_info is not None:
            error_result_kwargs["debug"] = debug_info

        error_result = AnalyzeResult(**error_result_kwargs)

        # 返回前日志：记录降级结果
        logger.info(f"[ANALYZE RESULT] relationship_stage={error_result.relationship_stage}, interest_level={error_result.interest_level}, degraded=True")

        return AnalysisResponse(
            request_id=request.request_id or str(uuid.uuid4()),
            status="error",
            result=error_result,
            error_message=str(e),
            metadata={
                "pipeline_version": "v3",
                "error": True,
                "debug_mode": request.debug,
            }
        )