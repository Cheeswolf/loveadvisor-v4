"""
LoveAdvisor V3 - Pipeline Orchestrator
Phase 1: Engineering Skeleton Initialization

This module orchestrates the execution of the LoveAdvisor V3 pipeline stages.
It coordinates services, manages error handling, and ensures data flows correctly
between preprocessing, signal extraction, strategy generation, and output building.
"""

import asyncio
import json
import logging
import traceback
from typing import Dict, Any, Optional
from enum import Enum

from app.prompts.s2_prompt import S2_SYSTEM_PROMPT, S2_PROMPT
from app.prompts.s3_prompt import S3_SYSTEM_PROMPT, S3_PROMPT
from app.parsers.s2_parser import parse_s2_response
from app.parsers.s3_parser import parse_s3_response
from app.llm.provider_factory import get_provider
from app.services.r1_service import infer_r1
from app.services.strategy_generator import generate_strategy_async
from app.services.guardrail_service import apply_guardrail
from app.utils.text_cleaner import clean_chat_text

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """
    Enum representing all pipeline stages in LoveAdvisor V3.

    The pipeline follows LoveAdvisor's business naming convention:
    1. PREPROCESS: Clean and enrich user input
    2. S2_BASIC_SIGNAL_EXTRACTION: Extract basic emotional and relational signals
    3. S3_ADVANCED_SIGNAL_EXTRACTION: Extract advanced relationship patterns
    4. R1_RULE_INFERENCE: Apply business rules for relationship assessment
    5. S5_STRATEGY_GENERATION: Generate personalized relationship strategies
    6. GUARDRAIL: Apply safety and ethical guardrails
    7. OUTPUT_BUILDING: Format final output with metadata
    """
    PREPROCESS = "preprocess"
    S2_BASIC_SIGNAL_EXTRACTION = "s2_basic_signal_extraction"
    S3_ADVANCED_SIGNAL_EXTRACTION = "s3_advanced_signal_extraction"
    R1_RULE_INFERENCE = "r1_rule_inference"
    S5_STRATEGY_GENERATION = "s5_strategy_generation"
    GUARDRAIL = "guardrail"
    OUTPUT_BUILDING = "output_building"


class PipelineOrchestrator:
    """
    Orchestrates the execution of the LoveAdvisor V3 analysis pipeline.

    The complete V3 pipeline consists of 7 stages following LoveAdvisor business naming:
    1. PREPROCESS: Clean, normalize, and enrich user input
    2. S2_BASIC_SIGNAL_EXTRACTION: Extract basic emotional and relational signals
    3. S3_ADVANCED_SIGNAL_EXTRACTION: Extract advanced relationship patterns and dynamics
    4. R1_RULE_INFERENCE: Apply business rules for relationship stage and interest assessment
    5. S5_STRATEGY_GENERATION: Generate personalized, actionable relationship strategies
    6. GUARDRAIL: Apply safety, ethical, and quality guardrails
    7. OUTPUT_BUILDING: Format final output with metadata and performance metrics

    Each stage is implemented as a separate service that can be developed,
    tested, and replaced independently.
    """

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with runtime context.

        Args:
            context: Runtime context containing request data and configuration.

        TODO: Initialize stage handlers, services, and dependencies.
        """
        self.context = context or {}
        self.stage_handlers = {}  # TODO: Initialize with actual stage handlers
        self.guardrail_service = None  # TODO: Initialize GuardrailService
        self.history_service = None  # TODO: Initialize HistoryService
        self.metrics_service = None  # TODO: Initialize MetricsService

    async def execute_full_pipeline(self) -> Dict[str, Any]:
        """
        Execute the complete 7-stage pipeline.

        Returns:
            Dictionary containing the final analysis results.

        Raises:
            PipelineError: If any stage fails or guardrails are violated.

        TODO: Implement complete pipeline execution with error handling and recovery.
        """
        # Stage 1: Preprocessing
        # TODO: Execute preprocessing stage (clean, normalize, enrich input)

        # Stage 2: S2 Basic Signal Extraction
        # TODO: Execute S2 basic signal extraction stage (extract emotional/relational signals)

        # Stage 3: S3 Advanced Signal Extraction
        # TODO: Execute S3 advanced signal extraction stage (extract relationship patterns)

        # Stage 4: R1 Rule Inference
        # TODO: Execute R1 rule inference stage (apply business rules for assessment)

        # Stage 5: S5 Strategy Generation
        # TODO: Execute S5 strategy generation stage (generate personalized advice)

        # Stage 6: Guardrail
        # TODO: Execute guardrail stage (apply safety and ethical checks)

        # Stage 7: Output Building
        # TODO: Execute output building stage (format final results with metadata)

        return {
            "status": "stub",
            "message": "Full pipeline execution not yet implemented",
            "stages_completed": 0,
            "pipeline_version": "v3"
        }

    async def execute_stage(self, stage: PipelineStage) -> Dict[str, Any]:
        """
        Execute a single pipeline stage.

        Args:
            stage: The pipeline stage to execute.

        Returns:
            Output of the specified stage.

        Raises:
            ValueError: If the stage is not recognized.
            StageExecutionError: If stage execution fails.

        TODO: Implement single stage execution with proper validation and error handling.
        """
        if stage not in self.stage_handlers:
            raise ValueError(f"Unknown pipeline stage: {stage}")

        # TODO: Execute the specified stage handler
        # TODO: Validate stage output
        # TODO: Update context with stage results
        # TODO: Collect metrics and telemetry

        return {
            "stage": stage.value,
            "status": "stub",
            "output": {},
            "metadata": {
                "execution_time": 0.0,
                "success": True,
                "errors": []
            }
        }

    async def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current status of the pipeline.

        Returns:
            Dictionary with pipeline status information.

        TODO: Implement comprehensive status reporting.
        """
        return {
            "pipeline_version": "v3",
            "stage_count": 7,
            "implemented_stages": 0,
            "services_initialized": False,
            "health_status": "unknown"
        }


# ============================================================================
# Simplified analysis pipeline for Phase 6 API + frontend integration
# ============================================================================

async def run_analysis_async(chat_text: str, user_question: str, provider_name: str = "mock", debug: bool = False) -> Dict[str, Any]:
    """
    Run the complete LoveAdvisor V3 analysis pipeline.

    This function orchestrates the full pipeline:
    1. S2 signal extraction
    2. S3 signal summary
    3. R1 rule inference
    4. S5 strategy generation
    5. Guardrail application

    Args:
        chat_text: The conversation text to analyze
        user_question: User's question or concern about the relationship
        provider_name: LLM provider name ("mock" or "deepseek")
        debug: If True, include intermediate results in output

    Returns:
        Dictionary containing the final analysis results with structure:
        - relationship_stage (str)
        - interest_level (str)
        - psychological_analysis (str)
        - risk_points (List[str])
        - suggestions (List[str])
        - next_step (str)
        - debug (optional Dict[str, Any] if debug=True)
    """
    logger.info(f"Starting analysis pipeline with provider={provider_name}, debug={debug}")
    # 调试：打印传入的 provider_name
    print(f"[后端-pipeline] 接收到的 provider_name: {provider_name}")

    # Validate chat_text is not empty
    if not chat_text or not isinstance(chat_text, str) or chat_text.strip() == "":
        logger.warning(f"chat_text is empty or invalid: {repr(chat_text)}")
        # Continue but note the issue in debug info

    # Preprocessing step
    cleaned_chat_text = chat_text
    preprocess_error_reason = None
    try:
        # Use the utility function directly
        cleaned_chat_text = clean_chat_text(chat_text)
    except Exception as e:
        preprocess_error_reason = str(e)
        logger.warning(f"Preprocessing failed: {e}")

    intermediate_results = {
        "raw_chat_text": chat_text,
        "cleaned_chat_text": cleaned_chat_text,
        "preprocess_error_reason": preprocess_error_reason,
        "s2_input_text": cleaned_chat_text,  # Use cleaned text for S2 input
        "provider_name": provider_name,
    }

    try:
        # Step 1: S2 Signal Extraction
        logger.info("Running S2 signal extraction...")
        s2_full_result = await _run_s2(cleaned_chat_text, provider_name)
        s2_raw_response = s2_full_result.get("raw_response")
        s2_parsed = s2_full_result.get("parsed", {})
        intermediate_results["s2_raw_response"] = s2_raw_response
        intermediate_results["s2_parsed"] = s2_parsed
        intermediate_results["s2"] = s2_parsed  # for backward compatibility

        # Step 2: S3 Signal Summary
        logger.info("Running S3 signal summary...")
        s3_full_result = await _run_s3(cleaned_chat_text, provider_name)
        s3_raw_response = s3_full_result.get("raw_response")
        s3_parsed = s3_full_result.get("parsed", {})
        intermediate_results["s3_raw_response"] = s3_raw_response
        intermediate_results["s3_parsed"] = s3_parsed
        intermediate_results["s3"] = s3_parsed  # for backward compatibility

        # Step 3: R1 Rule Inference
        logger.info("Running R1 rule inference...")
        r1_input = {"s2": s2_parsed, "s3": s3_parsed}
        r1_result = infer_r1(s2_parsed, s3_parsed, debug=debug)
        intermediate_results["r1_input"] = r1_input
        intermediate_results["r1_output"] = r1_result

        # Step 4: S5 Strategy Generation
        logger.info("Running S5 strategy generation...")
        s5_result = await generate_strategy_async(
            s2=s2_parsed,
            s3=s3_parsed,
            r1=r1_result,
            user_question=user_question,
            provider_name=provider_name
        )
        intermediate_results["s5_raw"] = s5_result

        # Step 5: Apply Guardrail
        logger.info("Applying guardrail corrections...")
        final_s5 = apply_guardrail(r1_result, s5_result)
        intermediate_results["s5_final"] = final_s5

        # Build final result
        result = {
            "relationship_stage": r1_result.get("relationship_stage", "无法判断"),
            "interest_level": r1_result.get("interest_level", "无法判断"),
            "psychological_analysis": final_s5.get("psychological_analysis", ""),
            "risk_points": final_s5.get("risk_points", []),
            "suggestions": final_s5.get("suggestions", []),
            "next_step": final_s5.get("next_step", ""),
        }

        # Add R1 debug fields if present (when debug=True)
        if debug:
            if "r1_debug_flags" in r1_result:
                result["r1_debug_flags"] = r1_result["r1_debug_flags"]
            if "r1_stage_reason" in r1_result:
                result["r1_stage_reason"] = r1_result["r1_stage_reason"]
            if "r1_interest_reason" in r1_result:
                result["r1_interest_reason"] = r1_result["r1_interest_reason"]
            # Add full debug info
            result["debug"] = intermediate_results

        logger.info(f"Analysis pipeline completed successfully. Relationship stage: {result['relationship_stage']}")
        return result

    except Exception as e:
        logger.error(f"Analysis pipeline failed: {e}", exc_info=True)

        # Determine pipeline error stage based on which intermediate results are available
        error_stage = "UNKNOWN"
        if "s2_raw_response" not in intermediate_results:
            error_stage = "S2_BASIC_SIGNAL_EXTRACTION"
        elif "s3_raw_response" not in intermediate_results:
            error_stage = "S3_ADVANCED_SIGNAL_EXTRACTION"
        elif "r1_output" not in intermediate_results:
            error_stage = "R1_RULE_INFERENCE"
        elif "s5_raw" not in intermediate_results:
            error_stage = "S5_STRATEGY_GENERATION"
        elif "s5_final" not in intermediate_results:
            error_stage = "GUARDRAIL"
        else:
            error_stage = "OUTPUT_BUILDING"

        # Create simplified traceback summary (limit to 500 chars)
        tb_summary = traceback.format_exc()
        if len(tb_summary) > 500:
            tb_summary = tb_summary[:497] + "..."

        # Add error information to intermediate_results for debug purposes
        intermediate_results["pipeline_error_stage"] = error_stage
        intermediate_results["pipeline_error_message"] = str(e)
        intermediate_results["traceback_summary"] = tb_summary

        # Return safe fallback result with debug info if requested
        fallback_result = {
            "relationship_stage": "无法判断",
            "interest_level": "无法判断",
            "psychological_analysis": "分析过程中出现错误，请稍后重试。",
            "risk_points": ["系统处理异常"],
            "suggestions": ["保持现状观察", "避免重大决定"],
            "next_step": "系统错误，建议暂停使用或联系支持",
        }

        if debug:
            fallback_result["debug"] = intermediate_results

        return fallback_result


async def _run_s2(conversation_text: str, provider_name: str) -> Dict[str, Any]:
    """
    Run S2 signal extraction using the specified LLM provider.

    Args:
        conversation_text: The conversation text to analyze
        provider_name: LLM provider name

    Returns:
        Dictionary containing:
        - raw_response: Raw LLM response text (or None for mock)
        - parsed: Parsed S2 signal dictionary
    """
    try:
        # Construct prompt
        prompt = S2_PROMPT.format(conversation_text=conversation_text)

        # Mock provider shortcut: return valid JSON for parsing
        if provider_name == "mock":
            # Return a mock S2 response dictionary that matches expected JSON structure
            # This will be directly parsed by parse_s2_response
            import sys
            print("DEBUG: Using mock S2 response", file=sys.stderr)
            mock_s2_response = {
                "initiative": "A 更主动",
                "response_length": "中",
                "emotional_tone": "温",
                "topic_depth": "中",
                "interaction_reciprocity": "正向承接",
                "key_signals": ["主动提问", "使用表情符号"]
            }
            return {
                "raw_response": None,  # No raw response for mock
                "parsed": mock_s2_response
            }

        # Get provider with default configuration
        provider = get_provider(provider_name)

        # Prepare request (using chat_complete for compatibility)
        messages = [
            {"role": "system", "content": S2_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        # Call provider directly with await
        response = await provider.chat_complete(messages, temperature=0.1, max_tokens=1000)
        response_text = response.text

        # Parse response
        parsed = parse_s2_response(response_text)
        return {
            "raw_response": response_text,
            "parsed": parsed
        }

    except Exception as e:
        logger.error(f"S2 execution failed: {e}", exc_info=True)
        # If error is about missing API key, re-raise to provide clear error message
        if isinstance(e, ValueError) and ("api_key" in str(e).lower() or "api key" in str(e).lower()):
            raise ValueError(f"DeepSeek API key not configured. Please set DEEPSEEK_API_KEY environment variable. Original error: {e}")
        # Return default S2 result
        default_parsed = {
            "initiative": "无法判断",
            "response_length": "无法判断",
            "emotional_tone": "无法判断",
            "topic_depth": "无法判断",
            "interaction_reciprocity": "无法判断",
            "key_signals": ["S2处理失败"]
        }
        return {
            "raw_response": f"S2 execution failed: {e}",
            "parsed": default_parsed
        }


def _count_conversation_turns(conversation_text: str) -> int:
    """
    计算对话文本中的轮数。

    对话文本格式通常为"A：xxx\\nB：xxx\\nA：xxx"。
    通过计算非空行数来估计对话轮数。
    """
    if not conversation_text or not isinstance(conversation_text, str):
        return 0

    # 按换行符分割，过滤空行和纯空白行
    lines = [line.strip() for line in conversation_text.splitlines()]
    non_empty_lines = [line for line in lines if line]

    # 每个非空行代表一个对话回合（发言）
    return len(non_empty_lines)


async def _run_s3(conversation_text: str, provider_name: str) -> Dict[str, Any]:
    """
    Run S3 signal summary using the specified LLM provider.

    Args:
        conversation_text: The conversation text to analyze
        provider_name: LLM provider name

    Returns:
        Dictionary containing:
        - raw_response: Raw LLM response text (or None for mock)
        - parsed: Parsed S3 summary dictionary
    """
    try:
        # Construct prompt
        prompt = S3_PROMPT.format(conversation_text=conversation_text)

        # Mock provider shortcut: return valid JSON for parsing
        if provider_name == "mock":
            # Return a mock S3 response dictionary that matches expected JSON structure
            # This will be directly parsed by parse_s3_response
            import sys
            print("DEBUG: Using mock S3 response", file=sys.stderr)
            mock_s3_response = {
                "has_intimacy_signal": True,
                "has_relationship_probe": False,
                "has_positive_reciprocity": True,
                "has_rejection_signal": False,
                "has_push_pull_pattern": False,
                "has_sustained_coldness": False,
                "signal_summary": ["双方互动积极，正向承接话题"]
            }
            # 即使是mock响应，也应用轮数检查规则
            turn_count = _count_conversation_turns(conversation_text)
            if turn_count <= 2:
                mock_s3_response["has_sustained_coldness"] = False
                mock_s3_response["has_rejection_signal"] = False
                logger.debug(f"Mock响应中强制设置has_sustained_coldness=False和has_rejection_signal=False，因为对话轮数={turn_count}≤2")
            return {
                "raw_response": None,  # No raw response for mock
                "parsed": mock_s3_response
            }

        # Get provider with default configuration
        provider = get_provider(provider_name)

        # Prepare request
        messages = [
            {"role": "system", "content": S3_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        # Call provider directly with await
        response = await provider.chat_complete(messages, temperature=0.1, max_tokens=1000)
        response_text = response.text

        # Parse response
        parsed = parse_s3_response(response_text)

        # 计算对话轮数，如果轮数≤2，强制has_sustained_coldness=False和has_rejection_signal=False
        # 持续冷淡需要多轮互动，单次短对话不能判定为冷淡期
        # 拒绝信号也需要多轮互动，单句短回复不能判定为拒绝
        turn_count = _count_conversation_turns(conversation_text)
        if turn_count <= 2:
            parsed["has_sustained_coldness"] = False
            parsed["has_rejection_signal"] = False
            logger.debug(f"强制设置has_sustained_coldness=False和has_rejection_signal=False，因为对话轮数={turn_count}≤2")

        return {
            "raw_response": response_text,
            "parsed": parsed
        }

    except Exception as e:
        logger.error(f"S3 execution failed: {e}", exc_info=True)
        # If error is about missing API key, re-raise to provide clear error message
        if isinstance(e, ValueError) and ("api_key" in str(e).lower() or "api key" in str(e).lower()):
            raise ValueError(f"DeepSeek API key not configured. Please set DEEPSEEK_API_KEY environment variable. Original error: {e}")
        # Return default S3 result
        default_parsed = {
            "has_intimacy_signal": False,
            "has_relationship_probe": False,
            "has_positive_reciprocity": False,
            "has_rejection_signal": False,
            "has_push_pull_pattern": False,
            "has_sustained_coldness": False,
            "signal_summary": ["S3处理失败"]
        }
        return {
            "raw_response": f"S3 execution failed: {e}",
            "parsed": default_parsed
        }


def run_analysis(chat_text: str, user_question: str, provider_name: str = "mock", debug: bool = False) -> Dict[str, Any]:
    """
    Synchronous wrapper for run_analysis_async.
    Uses asyncio.run() to call the async version.
    """
    import asyncio
    return asyncio.run(run_analysis_async(chat_text, user_question, provider_name, debug))