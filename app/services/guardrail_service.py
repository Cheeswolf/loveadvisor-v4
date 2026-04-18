"""
LoveAdvisor V3 - Guardrail Service
Phase 1: Engineering Skeleton Initialization

This service validates pipeline outputs against safety, ethical, and quality guardrails.
It ensures that all recommendations are appropriate, safe, and aligned with system guidelines.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from app.core.runtime_context import RuntimeContext
from app.core.enums import GuardrailSeverity


@dataclass
class GuardrailResult:
    """
    Result of guardrail validation.

    Attributes:
        passed: True if all guardrails passed, False otherwise
        violations: List of guardrail violations found
        severity: Highest severity level among violations
        adjusted_output: Optional adjusted output after guardrail application
    """
    passed: bool
    violations: List[Dict[str, Any]]
    severity: GuardrailSeverity
    adjusted_output: Optional[Dict[str, Any]] = None


class GuardrailService:
    """
    Service for validating outputs against guardrails.

    Guardrail categories:
    1. Safety guardrails: Prevent harmful or dangerous advice
    2. Ethical guardrails: Ensure ethical and responsible recommendations
    3. Quality guardrails: Maintain output quality and usefulness
    4. Legal guardrails: Comply with legal and regulatory requirements
    5. Cultural guardrails: Respect cultural sensitivities and norms
    """

    async def validate(self, output: Dict[str, Any], context: RuntimeContext) -> GuardrailResult:
        """
        Validate output against all applicable guardrails.

        Args:
            output: Pipeline output to validate.
            context: Runtime context for additional information.

        Returns:
            GuardrailResult indicating validation outcome.
        """
        violations = []

        # Check each guardrail category
        violations.extend(await self._check_safety_guardrails(output, context))
        violations.extend(await self._check_ethical_guardrails(output, context))
        violations.extend(await self._check_quality_guardrails(output, context))
        violations.extend(await self._check_legal_guardrails(output, context))
        violations.extend(await self._check_cultural_guardrails(output, context))

        # Determine overall result
        passed = len(violations) == 0
        severity = self._determine_max_severity(violations)

        # Apply corrections if needed
        adjusted_output = None
        if not passed:
            adjusted_output = await self._apply_corrections(output, violations, context)

        return GuardrailResult(
            passed=passed,
            violations=violations,
            severity=severity,
            adjusted_output=adjusted_output,
        )

    async def _check_safety_guardrails(
        self, output: Dict[str, Any], context: RuntimeContext
    ) -> List[Dict[str, Any]]:
        """
        Check safety guardrails.

        Safety guardrails prevent:
        - Advice that could cause physical harm
        - Encouragement of abusive behaviors
        - Recommendations that could worsen mental health
        - Suggestions that violate personal safety
        """
        violations = []
        # TODO: Implement safety guardrail checks
        return violations

    async def _check_ethical_guardrails(
        self, output: Dict[str, Any], context: RuntimeContext
    ) -> List[Dict[str, Any]]:
        """
        Check ethical guardrails.

        Ethical guardrails ensure:
        - Respect for autonomy and consent
        - Avoidance of manipulation or coercion
        - Protection of privacy and confidentiality
        - Fairness and non-discrimination
        """
        violations = []
        # TODO: Implement ethical guardrail checks
        return violations

    async def _check_quality_guardrails(
        self, output: Dict[str, Any], context: RuntimeContext
    ) -> List[Dict[str, Any]]:
        """
        Check quality guardrails.

        Quality guardrails maintain:
        - Relevance and appropriateness of advice
        - Clarity and understandability
        - Actionability and practicality
        - Evidence-based recommendations
        """
        violations = []
        # TODO: Implement quality guardrail checks
        return violations

    async def _check_legal_guardrails(
        self, output: Dict[str, Any], context: RuntimeContext
    ) -> List[Dict[str, Any]]:
        """
        Check legal guardrails.

        Legal guardrails ensure compliance with:
        - Professional licensing requirements
        - Healthcare regulations (where applicable)
        - Data protection laws
        - Consumer protection regulations
        """
        violations = []
        # TODO: Implement legal guardrail checks
        return violations

    async def _check_cultural_guardrails(
        self, output: Dict[str, Any], context: RuntimeContext
    ) -> List[Dict[str, Any]]:
        """
        Check cultural guardrails.

        Cultural guardrails respect:
        - Cultural norms and values
        - Religious sensitivities
        - Gender and sexuality considerations
        - Socioeconomic context
        """
        violations = []
        # TODO: Implement cultural guardrail checks
        return violations

    def _determine_max_severity(self, violations: List[Dict[str, Any]]) -> GuardrailSeverity:
        """
        Determine the maximum severity level among violations.

        Args:
            violations: List of violation dictionaries.

        Returns:
            Maximum severity level.
        """
        if not violations:
            return GuardrailSeverity.INFO

        severities = [v.get("severity", GuardrailSeverity.INFO) for v in violations]
        severity_order = {
            GuardrailSeverity.INFO: 0,
            GuardrailSeverity.WARNING: 1,
            GuardrailSeverity.BLOCKING: 2,
            GuardrailSeverity.SAFETY_CRITICAL: 3,
        }

        max_severity = max(severities, key=lambda s: severity_order.get(s, 0))
        return max_severity

    async def _apply_corrections(
        self,
        output: Dict[str, Any],
        violations: List[Dict[str, Any]],
        context: RuntimeContext,
    ) -> Dict[str, Any]:
        """
        Apply corrections to output based on guardrail violations.

        Args:
            output: Original output.
            violations: List of guardrail violations.
            context: Runtime context.

        Returns:
            Corrected output.
        """
        # TODO: Implement correction logic
        # For now, return original output with a note
        corrected = output.copy()
        corrected["guardrail_notes"] = {
            "violations_count": len(violations),
            "corrected": False,
            "note": "Guardrail corrections not yet implemented",
        }
        return corrected

    async def validate_input(self, user_input: str, user_context: Dict[str, Any]) -> GuardrailResult:
        """
        Validate user input before processing.

        Args:
            user_input: User input text.
            user_context: User-provided context.

        Returns:
            GuardrailResult for input validation.
        """
        violations = []

        # Check for inappropriate content
        if self._contains_inappropriate_content(user_input):
            violations.append({
                "type": "inappropriate_content",
                "severity": GuardrailSeverity.BLOCKING,
                "message": "Input contains inappropriate content",
                "details": {"offending_terms": self._extract_offending_terms(user_input)},
            })

        # Check for personal information
        if self._contains_personal_information(user_input):
            violations.append({
                "type": "personal_information",
                "severity": GuardrailSeverity.WARNING,
                "message": "Input may contain personal information",
                "details": {"suggestion": "Avoid sharing identifying details"},
            })

        passed = len(violations) == 0
        severity = self._determine_max_severity(violations)

        return GuardrailResult(
            passed=passed,
            violations=violations,
            severity=severity,
            adjusted_output=None,
        )

    def _contains_inappropriate_content(self, text: str) -> bool:
        """Check if text contains inappropriate content."""
        # TODO: Implement inappropriate content detection
        return False

    def _contains_personal_information(self, text: str) -> bool:
        """Check if text contains personal information."""
        # TODO: Implement personal information detection
        return False

    def _extract_offending_terms(self, text: str) -> List[str]:
        """Extract offending terms from text."""
        # TODO: Implement term extraction
        return []


# ============================================================================
# S5 Guardrail Function
# ============================================================================

def apply_guardrail(r1: Dict[str, Any], s5: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply guardrail checks and corrections to S5 output based on R1 results.

    This function provides the guardrail layer for S5 strategy generation.
    It ensures that S5 output aligns with R1 rule judgments and applies
    necessary corrections to prevent level-jumping or inappropriate advice.

    Args:
        r1: R1 rule inference result dictionary (must contain relationship_stage, interest_level, next_step_action)
        s5: S5 strategy generation result dictionary (must contain psychological_analysis, risk_points, suggestions, next_step)

    Returns:
        Guardrail-corrected S5 dictionary with same structure as input.

    Guardrail Checks:
    1. Stage boundary enforcement: Ensure suggestions don't encourage jumping relationship stages
    2. Interest level alignment: Ensure risk assessment matches interest level
    3. Next step consistency: Ensure next_step aligns with R1's next_step_action
    4. Safety checks: Remove unsafe or overly aggressive suggestions

    Important: Guardrail should NOT become a second R1. It only corrects
    S5 outputs, not re-judge relationship stage or interest level.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Create a copy to avoid modifying input
    corrected = s5.copy()

    # Validate inputs
    if not r1 or not isinstance(r1, dict):
        logger.warning("Invalid R1 input in guardrail, returning original S5")
        return corrected

    if not s5 or not isinstance(s5, dict):
        logger.warning("Invalid S5 input in guardrail, returning original")
        return corrected

    # Extract R1 fields with defaults
    r1_stage = r1.get("relationship_stage", "无法判断")
    r1_interest = r1.get("interest_level", "无法判断")
    r1_next_action = r1.get("next_step_action", "observe")

    # Ensure S5 has required fields
    if "psychological_analysis" not in corrected:
        corrected["psychological_analysis"] = "心理分析缺失"
    if "risk_points" not in corrected:
        corrected["risk_points"] = []
    if "suggestions" not in corrected:
        corrected["suggestions"] = []
    if "next_step" not in corrected:
        corrected["next_step"] = ""

    # Guardrail 1: Stage boundary enforcement
    corrected["suggestions"] = _enforce_stage_boundaries(
        r1_stage, corrected.get("suggestions", [])
    )

    # Guardrail 2: Interest level alignment for risk points
    corrected["risk_points"] = _adjust_risk_points_by_interest(
        r1_interest, corrected.get("risk_points", [])
    )

    # Guardrail 3: Next step consistency check
    corrected["next_step"] = _ensure_next_step_consistency(
        r1_stage, r1_next_action, corrected.get("next_step", "")
    )

    # Guardrail 4: Remove unsafe or aggressive suggestions
    corrected["suggestions"] = _filter_unsafe_suggestions(
        corrected.get("suggestions", [])
    )

    # Guardrail 5: Ensure psychological analysis doesn't contradict R1
    corrected["psychological_analysis"] = _ensure_analysis_alignment(
        r1_stage, r1_interest, corrected.get("psychological_analysis", "")
    )

    # Add guardrail metadata
    corrected["_guardrail_applied"] = True
    corrected["_guardrail_original_stage"] = r1_stage
    corrected["_guardrail_original_interest"] = r1_interest

    return corrected


def _enforce_stage_boundaries(stage: str, suggestions: List[str]) -> List[str]:
    """Enforce stage boundaries in suggestions."""
    if not suggestions:
        return suggestions

    # Define stage-inappropriate patterns for each stage
    inappropriate_patterns = {
        "初识期": [
            "表白", "确定关系", "见家长", "同居", "结婚",
            "发生关系", "亲密接触", "强烈追求", "猛烈追求",
            "每天联系", "频繁示爱", "直接问关系"
        ],
        "暧昧期": [
            "逼问关系", "强迫承诺", "要求明确答复", "施加压力",
            "威胁离开", "极端测试", "故意冷淡长时间"
        ],
        "拉扯期": [
            "过度妥协", "放弃原则", "无条件等待", "单方面付出",
            "容忍伤害", "牺牲自尊", "哀求挽回"
        ],
        "冷淡期": [
            "强行挽回", "死缠烂打", "不断质问", "情绪绑架",
            "威胁自残", "骚扰对方", "打扰亲友"
        ],
        "无法判断": [
            "重大决定", "关系承诺", "重大投入", "改变生活"
        ]
    }

    # Get patterns for current stage, fallback to all patterns
    patterns = inappropriate_patterns.get(stage, [])
    if stage not in inappropriate_patterns:
        patterns = []
        for stage_patterns in inappropriate_patterns.values():
            patterns.extend(stage_patterns)
        patterns = list(set(patterns))

    # Filter out inappropriate suggestions
    filtered_suggestions = []
    for suggestion in suggestions:
        suggestion_lower = suggestion.lower()
        is_inappropriate = False

        for pattern in patterns:
            if pattern in suggestion_lower:
                is_inappropriate = True
                break

        if not is_inappropriate:
            filtered_suggestions.append(suggestion)
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Filtered inappropriate suggestion for stage {stage}: {suggestion}")

    # Ensure we don't return empty list
    if not filtered_suggestions:
        if stage == "初识期":
            return ["保持自然轻松的互动", "观察对方回应模式"]
        elif stage == "暧昧期":
            return ["适度推进关系试探", "保持良好互动频率"]
        elif stage == "拉扯期":
            return ["保持情绪稳定和适当距离", "观察对方真实意图"]
        elif stage == "冷淡期":
            return ["降低期望和情感投入", "优先关注自我需求"]
        else:
            return ["保持观察，避免重大决定"]

    return filtered_suggestions


def _adjust_risk_points_by_interest(interest: str, risk_points: List[str]) -> List[str]:
    """Adjust risk points based on interest level."""
    if not risk_points:
        return risk_points

    adjusted_risk_points = risk_points.copy()

    # Add interest-specific risk points
    if interest == "低":
        if not any("兴趣低" in rp or "兴趣有限" in rp for rp in adjusted_risk_points):
            adjusted_risk_points.append("对方兴趣水平较低，关系推进难度大")
    elif interest == "高":
        # For high interest, ensure risk points aren't overly pessimistic
        overly_pessimistic = [
            "完全没兴趣", "毫无希望", "不可能成功", "绝对没戏",
            "彻底放弃", "死心吧", "别浪费时间"
        ]
        adjusted_risk_points = [
            rp for rp in adjusted_risk_points
            if not any(pessimistic in rp for pessimistic in overly_pessimistic)
        ]

    # Limit to 3 risk points max
    if len(adjusted_risk_points) > 3:
        adjusted_risk_points = adjusted_risk_points[:3]

    return adjusted_risk_points


def _ensure_next_step_consistency(stage: str, next_action: str, next_step: str) -> str:
    """Ensure next_step is consistent with R1's next_step_action."""
    if not next_step:
        # Generate default next step based on stage and action
        action_descriptions = {
            "observe": "继续观察互动模式",
            "hold": "暂不加码，维持现状",
            "light_reply": "轻度回应对方互动",
            "light_extend": "延续当前话题深度",
            "light_probe": "进行轻度关系试探",
            "follow_reciprocity": "顺势承接对方积极信号",
            "deescalate": "降低互动频率和强度",
            "step_back": "暂时后撤给予空间",
            "pause_contact": "暂停主动联系",
            "reduce_investment": "明确降低情感投入"
        }

        action_desc = action_descriptions.get(next_action, "继续观察")
        stage_context = {
            "初识期": f"在初识阶段，{action_desc}，重点建立基础好感。",
            "暧昧期": f"在暧昧阶段，{action_desc}，适度推进情感连接。",
            "拉扯期": f"在拉扯阶段，{action_desc}，保持平衡避免过度投入。",
            "冷淡期": f"在冷淡阶段，{action_desc}，保护自我情感健康。",
            "无法判断": f"在当前阶段，{action_desc}，收集更多信息再评估。"
        }.get(stage, f"{action_desc}。")

        return stage_context

    # Check if next_step contradicts the action
    contradictions = {
        "observe": ["强烈推进", "主动表白", "逼问关系", "施加压力"],
        "hold": ["加大投入", "增加频率", "推进关系", "主动升级"],
        "light_reply": ["过度回应", "长篇大论", "情感宣泄", "强烈表达"],
        "deescalate": ["增加联系", "加强追求", "主动推进", "升级关系"],
        "step_back": ["主动联系", "推进关系", "增加互动", "表达需求"],
        "pause_contact": ["继续联系", "主动沟通", "挽回努力", "保持互动"],
        "reduce_investment": ["增加付出", "继续等待", "坚持追求", "保持投入"]
    }

    action_contradictions = contradictions.get(next_action, [])
    next_step_lower = next_step.lower()

    has_contradiction = False
    for contradiction in action_contradictions:
        if contradiction in next_step_lower:
            has_contradiction = True
            break

    if has_contradiction:
        # Use default next step
        return _ensure_next_step_consistency(stage, next_action, "")

    return next_step


def _filter_unsafe_suggestions(suggestions: List[str]) -> List[str]:
    """Filter out unsafe or harmful suggestions."""
    if not suggestions:
        return suggestions

    unsafe_patterns = [
        "伤害自己", "自残", "自杀", "威胁", "恐吓",
        "骚扰", "跟踪", "偷窥", "侵犯隐私", "违法",
        "欺骗", " manipulation", "控制", "精神控制",
        "金钱勒索", "性勒索", "报复", "暴力",
        "药物控制", "酒精控制", "胁迫", "强迫"
    ]

    filtered = []
    for suggestion in suggestions:
        suggestion_lower = suggestion.lower()
        is_unsafe = False

        for pattern in unsafe_patterns:
            if pattern in suggestion_lower:
                is_unsafe = True
                break

        if not is_unsafe:
            filtered.append(suggestion)
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Filtered unsafe suggestion: {suggestion}")

    return filtered if filtered else ["保持健康安全的关系互动方式"]


def _ensure_analysis_alignment(stage: str, interest: str, analysis: str) -> str:
    """Ensure psychological analysis doesn't contradict R1 stage/interest."""
    if not analysis:
        return analysis

    # Check for contradictions
    contradictions = []

    if stage == "初识期" and ("深爱" in analysis or "热恋" in analysis or "亲密无间" in analysis):
        contradictions.append("分析过度乐观，与初识期不符")

    if stage == "冷淡期" and ("热情高涨" in analysis or "关系亲密" in analysis or "双向奔赴" in analysis):
        contradictions.append("分析过度乐观，与冷淡期不符")

    if interest == "低" and ("兴趣很高" in analysis or "非常喜欢" in analysis or "强烈好感" in analysis):
        contradictions.append("分析过度乐观，与低兴趣不符")

    if interest == "高" and ("毫无兴趣" in analysis or "完全没戏" in analysis or "彻底放弃" in analysis):
        contradictions.append("分析过度悲观，与高兴趣不符")

    if contradictions:
        # Keep original but add note
        return f"{analysis} (注：系统检测到分析可能与当前关系阶段/兴趣水平不完全一致，请谨慎参考)"

    return analysis