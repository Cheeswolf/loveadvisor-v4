"""
LoveAdvisor V3 - Strategy Generator Service
Phase 1: Engineering Skeleton Initialization

This service generates personalized advice and strategies based on extracted signals.
It translates signals into actionable recommendations using reasoning patterns.
"""

from typing import Dict, Any, List, Union
import json
import logging

from app.core.runtime_context import RuntimeContext
from app.core.enums import StrategyType
from app.prompts.s5_prompt import S5_SYSTEM_PROMPT, S5_PROMPT
from app.parsers.s5_parser import parse_s5_response, validate_s5_strategies
from app.llm.provider_factory import get_provider

logger = logging.getLogger(__name__)


class StrategyGenerator:
    """
    Service for generating personalized relationship strategies.

    Responsibilities:
    1. Match extracted signals to relevant strategy patterns
    2. Generate context-appropriate advice and recommendations
    3. Prioritize strategies based on urgency and impact
    4. Adapt strategies to user's cultural context and preferences
    5. Provide reasoning for each recommended strategy
    """

    async def execute(self, context: RuntimeContext) -> Dict[str, Any]:
        """
        Generate strategies based on extracted signals.

        Args:
            context: Runtime context containing extracted signals.

        Returns:
            Dictionary containing generated strategies with priorities.
        """
        # TODO: Implement actual strategy generation logic
        # This stub returns example strategies for skeleton purposes

        signal_data = context.get_stage_output("signal_extraction")
        if not signal_data:
            # Fallback if signal extraction didn't run
            signal_data = {"emotional_signals": [], "relational_signals": []}

        strategies = {
            "primary_strategies": self._generate_primary_strategies(signal_data),
            "secondary_strategies": self._generate_secondary_strategies(signal_data),
            "safety_strategies": self._generate_safety_strategies(signal_data),
            "strategy_metadata": {
                "generation_method": "stub",
                "total_strategies": 3,
                "priority_criteria": "urgency_and_impact",
            }
        }

        return strategies

    def _generate_primary_strategies(self, signal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate primary strategies addressing core issues.

        Args:
            signal_data: Extracted signal data.

        Returns:
            List of primary strategy dictionaries.
        """
        # TODO: Implement primary strategy generation
        return [
            {
                "type": StrategyType.ACTIVE_LISTENING,
                "title": "积极倾听练习",
                "description": "学习专注倾听伴侣的感受而不立即提供解决方案",
                "steps": [
                    "重复对方的话以确认理解",
                    "使用'我听到你说...'开头",
                    "避免打断或辩解",
                ],
                "priority": "high",
                "expected_impact": "改善沟通质量，减少误解",
                "time_commitment": "每天10-15分钟",
            },
            {
                "type": StrategyType.EMOTION_LABELING,
                "title": "情绪标注练习",
                "description": "帮助识别和命名自己的情绪，增加情绪意识",
                "steps": [
                    "当感到情绪波动时暂停",
                    "尝试用具体词汇描述情绪",
                    "记录情绪触发因素",
                ],
                "priority": "medium",
                "expected_impact": "提高情绪调节能力",
                "time_commitment": "每天5分钟",
            },
        ]

    def _generate_secondary_strategies(self, signal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate secondary strategies for ongoing improvement.

        Args:
            signal_data: Extracted signal data.

        Returns:
            List of secondary strategy dictionaries.
        """
        # TODO: Implement secondary strategy generation
        return [
            {
                "type": StrategyType.QUALITY_TIME,
                "title": "高质量相处时间",
                "description": "安排不受干扰的专属时间加强情感连接",
                "steps": [
                    "每周安排2-3次30分钟专属时间",
                    "关闭手机和电子设备",
                    "选择双方都享受的活动",
                ],
                "priority": "medium",
                "expected_impact": "增强情感亲密感",
                "time_commitment": "每周1-2小时",
            },
        ]

    def _generate_safety_strategies(self, signal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate safety strategies for high-risk situations.

        Args:
            signal_data: Extracted signal data.

        Returns:
            List of safety strategy dictionaries.
        """
        # TODO: Implement safety strategy generation
        # Check for safety concerns in signals
        has_safety_concerns = self._detect_safety_concerns(signal_data)

        if not has_safety_concerns:
            return []

        return [
            {
                "type": StrategyType.SUPPORT_SEEKING,
                "title": "寻求专业支持",
                "description": "联系专业心理咨询师或关系顾问",
                "steps": [
                    "查找本地心理咨询资源",
                    "预约初次咨询评估",
                    "准备要讨论的具体问题",
                ],
                "priority": "high",
                "expected_impact": "获得专业指导，确保安全",
                "time_commitment": "每周1小时",
                "safety_note": "如果感到威胁或危险，请立即联系当地支持热线",
            },
        ]

    def _detect_safety_concerns(self, signal_data: Dict[str, Any]) -> bool:
        """
        Detect safety concerns in extracted signals.

        Args:
            signal_data: Extracted signal data.

        Returns:
            True if safety concerns detected, False otherwise.
        """
        # TODO: Implement safety concern detection
        # Check for signals indicating abuse, manipulation, self-harm, etc.
        return False


# ============================================================================
# S5 Strategy Generation Function
# ============================================================================

async def generate_strategy_async(
    s2: Dict[str, Any],
    s3: Dict[str, Any],
    r1: Dict[str, Any],
    user_question: str,
    provider_name: str = "mock"
) -> Dict[str, Any]:
    """
    Generate S5 strategy based on S2, S3, R1 results and user question.

    This function provides the S5 strategy generation service layer.
    It constructs the S5 prompt, calls the provider, parses the response,
    and returns structured S5 results.

    Args:
        s2: S2 signal extraction result dictionary
        s3: S3 signal summary result dictionary
        r1: R1 rule inference result dictionary (must contain relationship_stage, interest_level, next_step_action)
        user_question: User's original question or concern
        provider_name: LLM provider name ("mock", "deepseek", "openai", etc.)

    Returns:
        Dictionary with S5 strategy fields:
        - psychological_analysis: str
        - risk_points: List[str]
        - suggestions: List[str]
        - next_step: str

    Raises:
        ValueError: If required inputs are missing or invalid
        RuntimeError: If LLM provider fails
    """
    # Validate inputs
    if not s2 or not isinstance(s2, dict):
        raise ValueError("s2 must be a non-empty dictionary")
    if not s3 or not isinstance(s3, dict):
        raise ValueError("s3 must be a non-empty dictionary")
    if not r1 or not isinstance(r1, dict):
        raise ValueError("r1 must be a non-empty dictionary")
    if not isinstance(user_question, str):
        logger.warning("user_question is not a string, using default question")
        user_question = "基于当前聊天情况，我应该如何推进关系？"
    elif not user_question.strip():
        logger.warning("user_question is empty string, using default question")
        user_question = "基于当前聊天情况，我应该如何推进关系？"

    # Check required R1 fields
    required_r1_fields = ["relationship_stage", "interest_level", "next_step_action"]
    for field in required_r1_fields:
        if field not in r1:
            logger.warning(f"R1 missing field '{field}', using default")
            r1[field] = "无法判断" if field != "next_step_action" else "observe"

    # Prepare data for prompt
    try:
        s2_json = json.dumps(s2, ensure_ascii=False, indent=2)
        s3_json = json.dumps(s3, ensure_ascii=False, indent=2)
        r1_json = json.dumps(r1, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to serialize input data: {e}")
        # Fallback to simple string representation
        s2_json = str(s2)
        s3_json = str(s3)
        r1_json = str(r1)

    # Construct prompt
    prompt = S5_PROMPT.format(
        s2_output=s2_json,
        s3_output=s3_json,
        r1_output=r1_json,
        user_question=user_question
    )

    try:
        # Get provider with default configuration
        provider = get_provider(provider_name)

        # Call provider (mock provider returns mock response, real providers make API call)
        if provider_name == "mock":
            # For mock provider, return a mock S5 response based on R1 stage
            mock_s5_response = _generate_mock_s5_response(r1)
            llm_response_text = json.dumps(mock_s5_response, ensure_ascii=False)
        else:
            # For real providers, make actual API call using chat_complete
            # Prepare messages
            messages = [
                {"role": "system", "content": S5_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            # Call provider directly with await
            try:
                response = await provider.chat_complete(messages, temperature=0.1, max_tokens=1500)
                llm_response_text = response.text
                logger.info(f"Successfully called provider {provider_name}, response length: {len(llm_response_text)}")
            except Exception as e:
                logger.error(f"Provider {provider_name} call failed: {e}", exc_info=True)
                # Fall back to mock response
                logger.warning(f"Falling back to mock response due to provider error")
                mock_s5_response = _generate_mock_s5_response(r1)
                llm_response_text = json.dumps(mock_s5_response, ensure_ascii=False)

        # Parse response
        parsed_s5 = parse_s5_response(llm_response_text)

        # Validate parsed data
        if not validate_s5_strategies(parsed_s5):
            logger.warning("S5 parsed data failed validation, using defaults")
            # Use parsed data anyway (parser already provides defaults)

        return parsed_s5

    except Exception as e:
        logger.error(f"S5 strategy generation failed: {e}", exc_info=True)
        # Return safe default
        return {
            "psychological_analysis": "系统生成策略时遇到错误，建议保持观察。",
            "risk_points": ["系统处理异常，建议谨慎对待"],
            "suggestions": ["保持现状观察", "避免重大关系决策"],
            "next_step": "系统错误，建议暂停使用或联系支持"
        }


def _generate_mock_s5_response(r1: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock S5 response based on R1 relationship stage."""
    stage = r1.get("relationship_stage", "无法判断")
    interest = r1.get("interest_level", "无法判断")
    next_action = r1.get("next_step_action", "observe")

    # Stage-based mock responses
    mock_responses = {
        "初识期": {
            "psychological_analysis": "当前处于关系初识阶段，双方了解有限。你的主动表现出一定的好感，但对方回应尚属礼貌范畴，需更多观察互动模式。",
            "risk_points": ["过早暴露需求可能降低吸引力", "对方兴趣水平尚不明确"],
            "suggestions": ["保持自然轻松的互动频率", "观察对方对话题的回应积极性", "避免连续追问或过度关注"],
            "next_step": "继续轻度互动，重点观察对方是否主动发起话题或深化对话。"
        },
        "暧昧期": {
            "psychological_analysis": "关系进入暧昧阶段，双方有明显好感信号。互动中存在情感表达和亲密暗示，但尚未明确关系状态。",
            "risk_points": ["关系状态未明可能导致期待落差", "推进过快可能引发对方退缩"],
            "suggestions": ["适度增加情感话题深度", "创造轻松独处机会加深了解", "观察对方对关系试探的反应"],
            "next_step": "在保持现有良好互动基础上，尝试轻度关系状态试探。"
        },
        "拉扯期": {
            "psychological_analysis": "关系呈现拉扯状态，混合亲近与疏远信号。对方可能处于矛盾心态，既有好感又有顾虑，导致互动不稳定。",
            "risk_points": ["情绪消耗较大可能影响心理健康", "关系不确定性高"],
            "suggestions": ["保持情绪稳定，避免过度解读单次互动", "设置明确的个人边界和期待值", "给双方适当空间减少压迫感"],
            "next_step": "暂时后撤观察，减少主动频率，重点看对方是否主动推进。"
        },
        "冷淡期": {
            "psychological_analysis": "关系进入冷淡阶段，互动明显减少且情感温度低。对方兴趣显著下降，可能已有疏远意图。",
            "risk_points": ["持续单向投入可能导致自我价值感降低", "关系修复难度较大"],
            "suggestions": ["显著降低联系频率和情感投入", "重新评估关系价值和可行性", "优先关注自我情感需求和心理健康"],
            "next_step": "暂停主动联系，专注自我生活，观察对方是否有主动修复意愿。"
        },
        "无法判断": {
            "psychological_analysis": "当前信号有限或矛盾，难以准确判断关系阶段。建议避免基于有限信息做出重大假设。",
            "risk_points": ["信息不足可能导致误判", "基于猜测的行动风险较高"],
            "suggestions": ["继续收集更多互动信号", "保持现状避免重大关系决策", "多角度观察对方行为模式"],
            "next_step": "维持当前互动水平，继续观察收集更多信息后再评估。"
        }
    }

    # Get response for stage or default
    response = mock_responses.get(stage, mock_responses["无法判断"])

    # Adjust based on interest level
    if interest == "低":
        response["risk_points"].append("对方兴趣水平较低，关系推进难度大")
        response["suggestions"].append("显著降低期望值，做好心理准备")
    elif interest == "高":
        response["suggestions"].append("可适度增加互动信心，但仍需循序渐进")

    # Adjust next_step based on next_action
    action_texts = {
        "observe": "继续观察",
        "hold": "暂不加码",
        "light_reply": "轻度回应即可",
        "light_extend": "延续当前话题",
        "light_probe": "轻度试探反馈",
        "follow_reciprocity": "顺势承接互动",
        "deescalate": "降低互动频率",
        "step_back": "暂时后撤观察",
        "pause_contact": "暂停主动联系",
        "reduce_investment": "明确降低投入"
    }

    action_text = action_texts.get(next_action, "继续观察")
    response["next_step"] = f"建议采取'{action_text}'策略，{response['next_step']}"

    return response


def generate_strategy(
    s2: Dict[str, Any],
    s3: Dict[str, Any],
    r1: Dict[str, Any],
    user_question: str,
    provider_name: str = "mock"
) -> Dict[str, Any]:
    """
    Synchronous wrapper for generate_strategy_async.
    Uses asyncio.run() to call the async version.
    """
    import asyncio
    return asyncio.run(generate_strategy_async(s2, s3, r1, user_question, provider_name))