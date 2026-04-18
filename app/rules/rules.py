# app/rules/rules.py
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Any, Dict, List, Optional


# =========================
# 基础工具函数
# =========================

def _safe_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _safe_list(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    return []


def _filter_functional_signals(key_signals: List[str]) -> List[str]:
    """
    过滤掉功能性信号，返回非功能性信号列表。
    功能性信号定义：包含以下任一关键词的信号：
    - "仅作简短确认"
    - "简短回应"
    - "单字回应"
    - "无信息量回应"
    如果 key_signals 仅包含功能性信号，则返回空列表。
    """
    if not key_signals:
        return []

    functional_keywords = [
        "仅作简短确认",
        "简短回应",
        "单字回应",
        "无信息量回应",
        "仅作简短事实性回应",
        "仅事实性回应",
        "未继续追问",
        "未推进",
        "未展开",
        "仅确认",
        "对话迅速结束",
        "弱承接",
        "简短事实性回应",
        "日常询问",
        "给予回应",
        "发起对话",
        "最低度回应",
    ]

    non_functional = []
    for signal in key_signals:
        signal_str = str(signal).strip()
        is_functional = False
        for keyword in functional_keywords:
            if keyword in signal_str:
                is_functional = True
                break
        if not is_functional:
            non_functional.append(signal_str)

    return non_functional


def is_low_quality_key_signals(key_signals: List[str]) -> bool:
    """
    判断 key_signals 是否全部为低质量信号。
    低质量信号包括：
    - 简短回应类：仅作简短确认、简短回应、单字回应、无信息量回应
    - 事实性回应类：仅作简短事实性回应、仅事实性回应、简短事实性回应
    - 未推进类：未继续追问、未推进、未展开、仅确认、对话迅速结束
    - 发起/回应类（无信息）：弱承接、最低度回应、日常询问、给予回应、发起对话、功能性回应、简单确认

    如果 key_signals 为空，返回 False（因为没有信号可判断）。
    如果所有信号都属于低质量类别，返回 True。
    如果有任何一个信号不属于低质量类别，返回 False。
    """
    if not key_signals:
        return False

    low_quality_keywords = [
        # 简短回应类
        "仅作简短确认", "简短回应", "单字回应", "无信息量回应",
        # 事实性回应类
        "仅作简短事实性回应", "仅事实性回应", "简短事实性回应",
        # 未推进类
        "未继续追问", "未推进", "未展开", "仅确认", "对话迅速结束",
        # 发起/回应类（无信息）
        "弱承接", "最低度回应", "日常询问", "给予回应", "发起对话", "功能性回应", "简单确认"
    ]

    for signal in key_signals:
        signal_str = str(signal).strip()
        is_low_quality = False
        for keyword in low_quality_keywords:
            if keyword in signal_str:
                is_low_quality = True
                break
        if not is_low_quality:
            # 发现一个非低质量信号
            return False

    # 所有信号都是低质量
    return True


def _norm_s2(s2: Dict[str, Any] | None) -> Dict[str, Any]:
    s2 = s2 or {}
    return {
        "initiative": _safe_str(s2.get("initiative", "无法判断")),
        "response_length": _safe_str(s2.get("response_length", "无法判断")),
        "emotional_tone": _safe_str(s2.get("emotional_tone", "无法判断")),
        "topic_depth": _safe_str(s2.get("topic_depth", "无法判断")),
        "interaction_reciprocity": _safe_str(s2.get("interaction_reciprocity", "无法判断")),
        "key_signals": [str(x).strip() for x in _safe_list(s2.get("key_signals")) if str(x).strip()],
    }


def _norm_s3(s3: Dict[str, Any] | None) -> Dict[str, Any]:
    s3 = s3 or {}
    return {
        "has_intimacy_signal": bool(s3.get("has_intimacy_signal", False)),
        "has_relationship_probe": bool(s3.get("has_relationship_probe", False)),
        "has_positive_reciprocity": bool(s3.get("has_positive_reciprocity", False)),
        "has_rejection_signal": bool(s3.get("has_rejection_signal", False)),
        "has_push_pull_pattern": bool(s3.get("has_push_pull_pattern", False)),
        "has_sustained_coldness": bool(s3.get("has_sustained_coldness", False)),
        "signal_summary": [str(x).strip() for x in _safe_list(s3.get("signal_summary")) if str(x).strip()],
    }


# =========================
# 高级信号辅助
# =========================

def has_any_advanced_signal(s3: Dict[str, Any], debug_info: Optional[Dict[str, Any]] = None) -> bool:
    result = any([
        s3.get("has_intimacy_signal", False),
        s3.get("has_relationship_probe", False),
        s3.get("has_positive_reciprocity", False),
        s3.get("has_rejection_signal", False),
        s3.get("has_push_pull_pattern", False),
        s3.get("has_sustained_coldness", False),
    ])
    if debug_info is not None:
        debug_info["has_any_advanced_signal"] = result
    return result


# =========================
# 可判性判断
# =========================

def is_low_information_density(s2: Dict[str, Any], debug_info: Optional[Dict[str, Any]] = None) -> bool:
    """
    判断是否为低信息密度对话（结构存在但信息为空）。
    满足以下任意条件 → 返回 True：
    1. 基础特征组合弱且无高级信号：
        - response_length == "短"
        - topic_depth == "浅"
        - interaction_reciprocity == "弱承接"
        - 无明确互动信号（追问、情绪表达、信息补充等）
    2. key_signals 仅包含低信息密度信号：
        - "仅作简短确认"
        - "简短回应"
        - "单字回应"
        - "无信息量回应"
        - "仅作简短事实性回应"
        - "仅事实性回应"
        - "未继续追问"
        - "未推进"
        - "未展开"
        - "仅确认"
        - "对话迅速结束"
        - "弱承接"
    并且：
    - 不包含任何明确互动信号：
        - 追问
        - 情绪表达
        - 信息补充
        - 正向承接
        - 明确回避
        - 热/冷情绪
        - 中/长回复
        - 中/深话题
        - 明确主动方（一方主动/双方接近）
    """
    response_length = s2.get("response_length")
    topic_depth = s2.get("topic_depth")
    interaction_reciprocity = s2.get("interaction_reciprocity")
    emotional_tone = s2.get("emotional_tone")
    initiative = s2.get("initiative")
    key_signals = [str(x).strip() for x in _safe_list(s2.get("key_signals")) if str(x).strip()]

    # 首先检查是否存在任何明确互动信号（如果有，则不是低信息密度）
    # 明确信号定义：
    has_clear_signal = (
        (initiative not in ["无法判断", "", None] and initiative is not None)  # 任何明确主动方
        or response_length in ["中", "长"]  # 中长回复
        or topic_depth in ["中", "深"]  # 中深话题
        or interaction_reciprocity in ["正向承接", "明确回避"]  # 明确承接或回避
        or emotional_tone in ["热", "冷"]  # 明确情绪
    )

    # 检查key_signals中是否包含明确互动信号
    # 注意：避免匹配低信息密度信号如"未继续追问"
    clear_keywords = ["情绪表达", "信息补充", "正向承接", "明确回避", "热", "冷"]
    for signal in key_signals:
        for keyword in clear_keywords:
            if keyword in signal:
                has_clear_signal = True
                break
        if has_clear_signal:
            break

    if has_clear_signal:
        # 存在明确互动信号，不是低信息密度
        if debug_info is not None:
            debug_info["is_low_information_density"] = False
        return False

    # 低信息密度信号关键词列表
    low_info_keywords = [
        "仅作简短确认",
        "简短回应",
        "单字回应",
        "无信息量回应",
        "仅作简短事实性回应",
        "仅事实性回应",
        "未继续追问",
        "未推进",
        "未展开",
        "仅确认",
        "对话迅速结束",
        "弱承接",
    ]

    # 检查 key_signals 是否仅包含低信息密度信号
    key_signals_only_low_info = True
    if key_signals:
        for signal in key_signals:
            is_low_info = False
            for keyword in low_info_keywords:
                if keyword in signal:
                    is_low_info = True
                    break
            if not is_low_info:
                key_signals_only_low_info = False
                break
    else:
        # 空列表视为仅包含低信息密度信号（无实质内容）
        key_signals_only_low_info = True

    # 条件1：key_signals 仅包含低信息密度信号
    if key_signals_only_low_info:
        # 如果key_signals仅包含低信息密度信号，无论基础特征如何，都是低信息密度
        if debug_info is not None:
            debug_info["is_low_information_density"] = True
        return True

    # 条件2：基础特征组合弱（短/浅/弱承接）且 key_signals 不包含明确互动信号
    # 检查是否满足基础特征组合
    basic_features_weak = (
        response_length == "短" and
        topic_depth == "浅" and
        interaction_reciprocity == "弱承接"
    )

    if basic_features_weak:
        # 基础特征弱，且已排除明确互动信号，视为低信息密度
        if debug_info is not None:
            debug_info["is_low_information_density"] = True
        return True

    # 条件3：基础特征部分弱（至少三个弱特征）且无明确互动信号
    weak_feature_count = 0
    if response_length == "短":
        weak_feature_count += 1
    if topic_depth == "浅":
        weak_feature_count += 1
    if interaction_reciprocity == "弱承接":
        weak_feature_count += 1
    if emotional_tone in ["温", "无法判断", ""]:
        weak_feature_count += 1
    if initiative in ["无法判断", "", None]:
        weak_feature_count += 1

    if weak_feature_count >= 4:  # 需要至少四个弱特征（总共五个特征）
        # 大多数特征都弱，视为低信息密度
        if debug_info is not None:
            debug_info["is_low_information_density"] = True
        return True

    # 不满足任何低信息密度条件
    if debug_info is not None:
        debug_info["is_low_information_density"] = False
    return False


def is_very_weak_s2(s2: Dict[str, Any], debug_info: Optional[Dict[str, Any]] = None) -> bool:
    initiative = s2.get("initiative")
    response_length = s2.get("response_length")
    emotional_tone = s2.get("emotional_tone")
    topic_depth = s2.get("topic_depth")
    interaction_reciprocity = s2.get("interaction_reciprocity")
    key_signals = _filter_functional_signals(_safe_list(s2.get("key_signals")))

    # 如果没有任何关键信号，视为非常弱
    if len(key_signals) == 0:
        if debug_info is not None:
            debug_info["is_very_weak_s2"] = True
        return True

    unknown_count = sum([
        initiative == "无法判断",
        response_length == "无法判断",
        emotional_tone == "无法判断",
        topic_depth == "无法判断",
        interaction_reciprocity == "无法判断",
    ])

    if unknown_count >= 3 and len(key_signals) <= 1:
        if debug_info is not None:
            debug_info["is_very_weak_s2"] = True
        return True

    # 只有当互动特征极其有限，且连主动方都不明确时，才视为非常弱
    if (
        initiative in ["无法判断", ""]
        and response_length in ["短", "无法判断", ""]
        and topic_depth in ["浅", "无法判断", ""]
        and interaction_reciprocity in ["弱承接", "无法判断", ""]
        and emotional_tone in ["温", "无法判断", "", "冷"]
        and len(key_signals) <= 1
    ):
        if debug_info is not None:
            debug_info["is_very_weak_s2"] = True
        return True

    result = False
    if debug_info is not None:
        debug_info["is_very_weak_s2"] = result
    return result


def is_functional_minimal_interaction(s2: Dict[str, Any], s3: Dict[str, Any], debug_info: Optional[Dict[str, Any]] = None) -> bool:
    """
    判断是否为功能性最低限度互动（真无法判断场景）：
    - 无高级信号
    - S2 信号极其微弱（接近无对话/单句/信息极少）
    - 若存在任何明确的基础互动信号（如 initiative 明确、reciprocity 明确等），则不视为最低限度互动
    """
    if has_any_advanced_signal(s3, debug_info):
        if debug_info is not None:
            debug_info["is_functional_minimal_interaction"] = False
        return False

    initiative = s2.get("initiative")
    response_length = s2.get("response_length")
    topic_depth = s2.get("topic_depth")
    reciprocity = s2.get("interaction_reciprocity")
    emotional_tone = s2.get("emotional_tone")
    key_signals = _filter_functional_signals(_safe_list(s2.get("key_signals")))

    # 检查是否存在任何明确的基础互动信号
    # 只有真正表明互动的值才视为明确信号，默认值（短/浅/弱承接/温）不视为明确信号
    has_any_clear_signal = (
        (initiative not in ["无法判断", "", "双方接近"] and initiative is not None)  # 双方接近可能是默认值？
        or response_length in ["中", "长"]  # 只有中长回复才视为明确信号
        or topic_depth in ["中", "深"]  # 只有中深话题才视为明确信号
        or reciprocity in ["正向承接", "明确回避"]  # 只有明确承接或回避才视为明确信号
        or emotional_tone in ["热", "冷"]  # 只有热或冷才视为明确信号，温不算
    )

    # 如果有明确信号，则不是最低限度互动
    if has_any_clear_signal:
        if debug_info is not None:
            debug_info["is_functional_minimal_interaction"] = False
        return False

    # 如果有任何关键信号，说明有一些互动痕迹，不是最低限度互动
    if len(key_signals) > 0:
        if debug_info is not None:
            debug_info["is_functional_minimal_interaction"] = False
        return False

    # 剩余情况：所有S2字段都是"无法判断"/空/默认值，且没有任何关键信号
    # 这是真正的信息极少场景
    unknown_count = sum([
        initiative in ["无法判断", "", None],
        response_length in ["无法判断", "", None],
        topic_depth in ["无法判断", "", None],
        reciprocity in ["无法判断", "", None],
        emotional_tone in ["无法判断", "", "温", None],
    ])

    # 所有字段都是未知/默认值，且无关键信号
    if unknown_count >= 4:
        if debug_info is not None:
            debug_info["is_functional_minimal_interaction"] = True
        return True

    if debug_info is not None:
        debug_info["is_functional_minimal_interaction"] = False
    return False


def is_judgable(s2: Dict[str, Any], s3: Dict[str, Any], debug_info: Optional[Dict[str, Any]] = None) -> bool:
    # 低信息密度过滤层
    if is_low_information_density(s2, debug_info):
        if debug_info is not None:
            debug_info["is_judgable"] = False
        return False

    if has_any_advanced_signal(s3, debug_info):
        if debug_info is not None:
            debug_info["is_judgable"] = True
        return True

    # 即使我们知道结果，也调用这两个函数来收集调试标志
    is_very_weak = is_very_weak_s2(s2, debug_info)
    is_minimal = is_functional_minimal_interaction(s2, s3, debug_info)

    if is_very_weak or is_minimal:
        if debug_info is not None:
            debug_info["is_judgable"] = False
        return False

    # 检查是否有足够的基础互动信号
    # 如果没有明确的基础互动信号，则不可判断
    initiative = s2.get("initiative")
    response_length = s2.get("response_length")
    topic_depth = s2.get("topic_depth")
    reciprocity = s2.get("interaction_reciprocity")
    emotional_tone = s2.get("emotional_tone")
    key_signals = _filter_functional_signals(_safe_list(s2.get("key_signals")))

    # 检查是否满足弱信号组合条件（E2/E3修复）
    # 在无高级信号前提下，若同时满足以下条件，默认不直接视为可判断
    is_all_weak_signals = (
        response_length == "短"
        and topic_depth == "浅"
        and reciprocity == "弱承接"
        and emotional_tone in ["温", "无法判断", ""]
        and initiative == "A更主动"
    )

    # 如果满足弱信号组合，则需要更强基础互动信号才允许进入"初识期"
    # 更强信号定义：
    # 1. response_length in ["中", "长"]
    # 2. topic_depth in ["中", "深"]
    # 3. reciprocity in ["正向承接", "明显回避"]
    # 4. key_signals 中存在非功能性、非事实性、非未推进类信号
    if is_all_weak_signals:
        # 检查是否有更强基础互动信号
        has_stronger_signal = (
            response_length in ["中", "长"]
            or topic_depth in ["中", "深"]
            or reciprocity in ["正向承接", "明显回避"]
        )

        # 检查 key_signals 中是否存在非功能性、非事实性、非未推进类信号
        # 功能性信号已经在 _filter_functional_signals 中过滤，这里检查剩余信号
        # E3修复：key_signals 可能全部是低质量信号，不能视为有效信号
        has_non_functional_key_signal = (
            len(key_signals) > 0
            and not is_low_quality_key_signals(key_signals)
        )

        if not (has_stronger_signal or has_non_functional_key_signal):
            # 没有更强信号，不可判断
            if debug_info is not None:
                debug_info["is_judgable"] = False
                debug_info["is_all_weak_signals"] = True
            return False

    # 明确的基础互动信号定义
    has_clear_signal = (
        (initiative not in ["无法判断", "", "双方接近"] and initiative is not None)
        or response_length in ["中", "长"]
        or topic_depth in ["中", "深"]
        or reciprocity in ["正向承接", "明确回避"]
        or emotional_tone in ["热", "冷"]
        or len(key_signals) > 0
    )

    if not has_clear_signal:
        if debug_info is not None:
            debug_info["is_judgable"] = False
        return False

    # 存在基础互动信号，可判断为初识期
    if debug_info is not None:
        debug_info["is_judgable"] = True
        if is_all_weak_signals:
            debug_info["is_all_weak_signals"] = True
    return True


# =========================
# relationship_stage
# =========================

def infer_relationship_stage(s2: Dict[str, Any], s3: Dict[str, Any], debug_info: Optional[Dict[str, Any]] = None) -> str:
    """
    优先级：
    无法判断 -> 暧昧期 -> 拉扯期 -> 冷淡期 -> 初识期
    """
    if not is_judgable(s2, s3, debug_info):
        if debug_info is not None:
            debug_info["stage_reason"] = "不可判断：缺少足够信号"
        return "无法判断"

    # 暧昧期：明确亲密且没有明显后退
    if (
        s3["has_intimacy_signal"]
        and not s3["has_rejection_signal"]
        and not s3["has_push_pull_pattern"]
        and not s3["has_sustained_coldness"]
    ):
        if debug_info is not None:
            debug_info["stage_reason"] = "暧昧期：有明确亲密信号且无拒绝/拉扯/持续冷淡"
        return "暧昧期"

    # 暧昧期：关系试探 + 正向承接，即使有轻微犹疑，也先归暧昧
    # 用来保住 B3，不轻易掉到拉扯
    if (
        s3["has_relationship_probe"]
        and s3["has_positive_reciprocity"]
        and not s3["has_push_pull_pattern"]
        and not s3["has_sustained_coldness"]
    ):
        if debug_info is not None:
            debug_info["stage_reason"] = "暧昧期：有关系试探和正向承接，且无拉扯/持续冷淡"
        return "暧昧期"

    # 拉扯期：必须更明确地出现推进+后退
    if s3["has_push_pull_pattern"]:
        if debug_info is not None:
            debug_info["stage_reason"] = "拉扯期：有明确的推拉模式信号"
        return "拉扯期"

    if s3["has_intimacy_signal"] and s3["has_rejection_signal"]:
        if debug_info is not None:
            debug_info["stage_reason"] = "拉扯期：既有亲密信号又有拒绝信号"
        return "拉扯期"

    if (
        s3["has_relationship_probe"]
        and s3["has_rejection_signal"]
        and not s3["has_positive_reciprocity"]
    ):
        if debug_info is not None:
            debug_info["stage_reason"] = "拉扯期：有关系试探但被拒绝，且无正向承接"
        return "拉扯期"

    # 冷淡期（C1修复：增加排除条件）
    # 检查是否存在关系变化关注/关系追问/回避解释等语境
    has_relationship_context = False
    signal_summary = s3.get("signal_summary", [])
    key_signals = s2.get("key_signals", [])

    # 检查 signal_summary 和 key_signals 中是否包含关系相关语境
    relationship_keywords = ["关系变化", "关系追问", "回避解释", "关系试探", "关系关注"]
    all_signals = [str(x).strip() for x in signal_summary + key_signals if str(x).strip()]

    for signal in all_signals:
        for keyword in relationship_keywords:
            if keyword in signal:
                has_relationship_context = True
                break
        if has_relationship_context:
            break

    # 新增拉扯期分支：有拒绝信号且存在关系变化关注/关系追问/回避解释等语境
    # D1修复：收紧条件，需要至少两个明确关系信号
    if s3["has_rejection_signal"] and has_relationship_context:
        # 计算明确关系信号数量
        relationship_signal_count = 0
        # 1. 明确关系变化追问
        if any("关系变化" in signal or "关系追问" in signal for signal in all_signals):
            relationship_signal_count += 1
        # 2. 明确关系解释回避
        if any("回避解释" in signal for signal in all_signals):
            relationship_signal_count += 1
        # 3. has_relationship_probe
        if s3["has_relationship_probe"]:
            relationship_signal_count += 1
        # 4. has_push_pull_pattern
        if s3["has_push_pull_pattern"]:
            relationship_signal_count += 1

        if relationship_signal_count >= 2:
            if debug_info is not None:
                debug_info["stage_reason"] = "拉扯期：有拒绝信号且存在至少两个明确关系信号"
            return "拉扯期"
        # 否则继续，可能落入冷淡期

    # 分支1：has_sustained_coldness
    if s3["has_sustained_coldness"]:
        # 如果有关系相关语境，优先考虑拉扯期而非冷淡期
        if has_relationship_context:
            # D1修复：需要至少两个明确关系信号才优先拉扯期
            # 计算明确关系信号数量
            relationship_signal_count = 0
            # 1. 明确关系变化追问
            if any("关系变化" in signal or "关系追问" in signal for signal in all_signals):
                relationship_signal_count += 1
            # 2. 明确关系解释回避
            if any("回避解释" in signal for signal in all_signals):
                relationship_signal_count += 1
            # 3. has_relationship_probe
            if s3["has_relationship_probe"]:
                relationship_signal_count += 1
            # 4. has_push_pull_pattern
            if s3["has_push_pull_pattern"]:
                relationship_signal_count += 1

            if relationship_signal_count < 2:
                # 关系信号不足，保持冷淡期
                if debug_info is not None:
                    debug_info["stage_reason"] = "冷淡期：有持续冷淡信号且关系信号不足"
                return "冷淡期"
            # 否则继续，可能落入拉扯期
        else:
            if debug_info is not None:
                debug_info["stage_reason"] = "冷淡期：有持续冷淡信号"
            return "冷淡期"

    # 分支2：has_rejection_signal + emotional_tone == "冷"
    if s3["has_rejection_signal"] and s2["emotional_tone"] == "冷":
        # 如果对话中包含关系试探/关系变化追问语义，应优先落入拉扯期
        if has_relationship_context:
            # D1修复：需要至少两个明确关系信号才优先拉扯期
            # 计算明确关系信号数量
            relationship_signal_count = 0
            # 1. 明确关系变化追问
            if any("关系变化" in signal or "关系追问" in signal for signal in all_signals):
                relationship_signal_count += 1
            # 2. 明确关系解释回避
            if any("回避解释" in signal for signal in all_signals):
                relationship_signal_count += 1
            # 3. has_relationship_probe
            if s3["has_relationship_probe"]:
                relationship_signal_count += 1
            # 4. has_push_pull_pattern
            if s3["has_push_pull_pattern"]:
                relationship_signal_count += 1

            if relationship_signal_count < 2:
                # 关系信号不足，保持冷淡期
                if debug_info is not None:
                    debug_info["stage_reason"] = "冷淡期：有拒绝信号且情绪语调为冷，关系信号不足"
                return "冷淡期"
            # 否则继续，可能落入拉扯期
        else:
            if debug_info is not None:
                debug_info["stage_reason"] = "冷淡期：有拒绝信号且情绪语调为冷"
            return "冷淡期"

    # 分支3：明显回避 + 冷情绪
    if (
        s2["interaction_reciprocity"] == "明显回避"
        and s2["emotional_tone"] == "冷"
    ):
        # 如果对话中包含关系试探/关系变化追问语义，应优先落入拉扯期
        if has_relationship_context:
            # D1修复：需要至少两个明确关系信号才优先拉扯期
            # 计算明确关系信号数量
            relationship_signal_count = 0
            # 1. 明确关系变化追问
            if any("关系变化" in signal or "关系追问" in signal for signal in all_signals):
                relationship_signal_count += 1
            # 2. 明确关系解释回避
            if any("回避解释" in signal for signal in all_signals):
                relationship_signal_count += 1
            # 3. has_relationship_probe
            if s3["has_relationship_probe"]:
                relationship_signal_count += 1
            # 4. has_push_pull_pattern
            if s3["has_push_pull_pattern"]:
                relationship_signal_count += 1

            if relationship_signal_count < 2:
                # 关系信号不足，保持冷淡期
                if debug_info is not None:
                    debug_info["stage_reason"] = "冷淡期：互动承接为明显回避且情绪语调为冷，关系信号不足"
                return "冷淡期"
            # 否则继续，可能落入拉扯期
        else:
            if debug_info is not None:
                debug_info["stage_reason"] = "冷淡期：互动承接为明显回避且情绪语调为冷"
            return "冷淡期"

    # E2/E3修复：极弱信号组合且无高级信号时，不应落入初识期
    if not has_any_advanced_signal(s3) and \
       s2["response_length"] == "短" and \
       s2["topic_depth"] == "浅" and \
       s2["interaction_reciprocity"] == "弱承接" and \
       s2["emotional_tone"] in ["温", "无法判断", ""]:
        # 检查 key_signals 和 signal_summary 是否全部属于低信息密度信号
        low_info_keywords = [
            "仅作简短确认", "简短确认", "简短回应", "单字回应", "无信息量回应",
            "仅作简短事实性回应", "仅事实性回应", "简短事实性回应",
            "未继续追问", "未推进", "未展开", "仅确认", "对话迅速结束",
            "弱承接", "发起对话", "发起话题", "主动发起",
            "回应简短无扩展", "日常信息交换", "对话简短", "仅为日常信息交换",
            "未识别出任何高级关系信号", "简短、礼貌", "初次问候"
        ]
        key_signals = s2.get("key_signals", [])
        signal_summary = s3.get("signal_summary", [])
        all_signals = [str(x).strip() for x in key_signals + signal_summary if str(x).strip()]
        all_low_info = True
        for signal in all_signals:
            is_low = False
            for keyword in low_info_keywords:
                if keyword in signal:
                    is_low = True
                    break
            if not is_low:
                all_low_info = False
                break
        if all_low_info:
            if debug_info is not None:
                debug_info["stage_reason"] = "无法判断：极弱信号组合且全部为低信息密度信号"
            return "无法判断"

    if debug_info is not None:
        debug_info["stage_reason"] = "初识期：可判断但不符合其他阶段特征"
    return "初识期"


# =========================
# interest_level 辅助
# =========================

def _initial_medium_signal(s2: Dict[str, Any], s3: Dict[str, Any]) -> bool:
    """
    初识期给中：
    收紧触发条件，避免礼貌回应、浅层互动、弱承接被抬到"中"。
    要求：
    1. 至少两个正向信号（同原规则）
    2. 无明确负向信号（拒绝、明显回避、冷情绪、持续冷淡）
    3. 互动强度足够：response_length不为"短"或interaction_reciprocity不为"弱承接"
    4. 加强正向承接与后退信号联动：如有拒绝信号，需更强正向信号补偿

    目标：
    - 压住 A1
    - 准确判断 A2 / A3 边界
    """
    # 负向信号检查：存在任何明确负向信号，直接排除中兴趣
    has_negative_signal = (
        s3["has_rejection_signal"]
        or s2["emotional_tone"] == "冷"
        or s2["interaction_reciprocity"] == "明显回避"
        or s3["has_sustained_coldness"]
    )
    if has_negative_signal:
        return False

    # 互动强度检查：避免弱承接+短回复的组合被抬到中兴趣
    # 如果两者都弱，则需要更强正向信号补偿
    weak_interaction = (
        s2["response_length"] == "短"
        and s2["interaction_reciprocity"] == "弱承接"
    )

    # 正向信号计分
    score = 0

    if s3["has_relationship_probe"]:
        score += 1

    if s3["has_positive_reciprocity"]:
        score += 2

    if s2["emotional_tone"] == "热":
        score += 1

    if s2["topic_depth"] in ["中", "深"]:
        score += 1

    if s2["interaction_reciprocity"] == "正向承接":
        score += 1

    # 基础要求：至少两个正向信号
    if score < 2:
        return False

    # 最小补偿分支：弱互动但有真实正向互惠的边界样本（A2/A3修复）
    if weak_interaction and s3["has_positive_reciprocity"]:
        # 已满足：无负向信号、score >= 2
        # 直接允许通过，避免被后续规则过度压制
        return True

    # 如果互动弱且没有正向承接，即使有两个正向信号也不给中
    # 例如：只有relationship_probe + topic_depth中深，但互动弱无正向承接
    # 补偿条件：如果存在正向承接，则允许弱互动下的边界样本
    if weak_interaction and not s3["has_positive_reciprocity"] and s2["interaction_reciprocity"] != "正向承接":
        return False

    # 如果有拒绝信号（但前面已排除），这里处理其他后退信号
    # 暂不额外处理

    return True


def _ambiguous_high_signal(s2: Dict[str, Any], s3: Dict[str, Any], relationship_stage: str) -> bool:
    """
    暧昧期给高：
    必须是明确双向靠近，不能只因为轻度 intimacy 就给高。
    目标：
    - 压住 B2
    - 尽量保住 B1
    """
    if relationship_stage != "暧昧期":
        return False

    if s3["has_rejection_signal"] or s3["has_push_pull_pattern"] or s3["has_sustained_coldness"]:
        return False

    # 基础门槛：必须同时有 intimacy + reciprocity
    if not (s3["has_intimacy_signal"] and s3["has_positive_reciprocity"]):
        return False

    # 再要求至少两个更强支撑
    strong_score = 0

    if s2["emotional_tone"] == "热":
        strong_score += 1

    if s2["response_length"] in ["中", "长"]:
        strong_score += 1

    if s2["initiative"] == "双方接近":
        strong_score += 1

    return strong_score >= 2


def _pull_low_signal(s2: Dict[str, Any], s3: Dict[str, Any]) -> bool:
    """
    拉扯期给低：
    只在明显失衡时给低。
    目标：
    - 避免 C1 被压成低
    - 保住 C3 的低兴趣边界
    """
    if not s3["has_rejection_signal"]:
        return False

    # 只要还有明确正向承接，就不要轻易给低
    if s3["has_positive_reciprocity"]:
        return False

    # C1修复：冲突型拉扯（情绪参与型拉扯）即使有拒绝信号+冷情绪+明显回避，但存在关系上下文时不应判为低兴趣
    if (
        s3["has_rejection_signal"]
        and s2["emotional_tone"] == "冷"
        and s2["interaction_reciprocity"] == "明显回避"
    ):
        # 检查是否存在关系上下文
        relationship_keywords = ["关系变化", "关系追问", "回避解释", "关系试探", "关系关注"]
        signal_summary = s3.get("signal_summary", [])
        key_signals = s2.get("key_signals", [])
        all_signals = [str(x).strip() for x in signal_summary + key_signals if str(x).strip()]

        has_relationship_context = False
        for signal in all_signals:
            for keyword in relationship_keywords:
                if keyword in signal:
                    has_relationship_context = True
                    break
            if has_relationship_context:
                break

        if has_relationship_context:
            # 情绪参与型拉扯，不应判为低兴趣
            return False

    cold_score = 0

    if s2["interaction_reciprocity"] == "明显回避":
        cold_score += 1

    if s2["emotional_tone"] == "冷":
        cold_score += 1

    if s3["has_sustained_coldness"]:
        cold_score += 1

    return cold_score >= 2


def _pull_medium_signal(s2: Dict[str, Any], s3: Dict[str, Any]) -> bool:
    """
    拉扯期给中（V3稳定化修复：进一步收紧门槛）：
    只有满足以下至少一项，才给"中"：
    1. has_positive_reciprocity = true
    2. response_length in ["中", "长"]
    3. interaction_reciprocity = "正向承接"

    若仅有以下信号但 response_length = "短" 且 interaction_reciprocity = "弱承接"
    且 has_positive_reciprocity = false，则兴趣等级应为"低"：
    - has_push_pull_pattern = true
    - has_intimacy_signal = true
    - has_relationship_probe = true

    C1修复：冲突型拉扯（情绪参与型拉扯）即使没有正向承接，也允许判为"中兴趣"
    条件收紧：
    - s3["has_rejection_signal"] == True
    - s2["emotional_tone"] == "冷"
    - s2["interaction_reciprocity"] == "明显回避"
    - 存在关系上下文（关系追问/关系变化）且至少两个关系信号
    - 互动强度足够：response_length不为"短"或interaction_reciprocity不为"弱承接"

    加强正向承接与后退信号联动：如果有拒绝信号，即使有正向承接，也需要额外正向信号补偿。
    """
    # C1修复：检查是否为冲突型拉扯（情绪参与型拉扯）
    # 如果满足条件，即使没有正向承接也允许判为中兴趣
    if (
        s3["has_rejection_signal"]
        and s2["emotional_tone"] == "冷"
        and s2["interaction_reciprocity"] == "明显回避"
    ):
        # 检查是否存在关系上下文
        relationship_keywords = ["关系变化", "关系追问", "回避解释", "关系试探", "关系关注"]
        signal_summary = s3.get("signal_summary", [])
        key_signals = s2.get("key_signals", [])
        all_signals = [str(x).strip() for x in signal_summary + key_signals if str(x).strip()]

        # 计算关系信号数量
        relationship_signal_count = 0
        for signal in all_signals:
            for keyword in relationship_keywords:
                if keyword in signal:
                    relationship_signal_count += 1
                    break  # 每个信号只计一次

        # 同时检查是否有has_relationship_probe或has_push_pull_pattern
        if s3["has_relationship_probe"]:
            relationship_signal_count += 1
        if s3["has_push_pull_pattern"]:
            relationship_signal_count += 1

        # 收紧条件：需要至少一个关系信号，且互动强度足够
        if relationship_signal_count >= 1:
            # 互动强度检查：避免弱互动下的冲突型拉扯被抬到中兴趣
            weak_interaction = (
                s2["response_length"] == "短"
                and s2["interaction_reciprocity"] == "弱承接"
            )
            if not weak_interaction:
                # 情绪参与型拉扯，应判为中兴趣
                return True

    if _pull_low_signal(s2, s3):
        return False

    # 收紧条件：必须满足以下至少一项才给中
    has_required_signal = (
        s3["has_positive_reciprocity"]
        or s2["response_length"] in ["中", "长"]
        or s2["interaction_reciprocity"] == "正向承接"
    )

    if not has_required_signal:
        return False

    # 加强正向承接与后退信号联动
    # 如果有拒绝信号，即使有正向承接，也需要额外正向信号补偿
    if s3["has_rejection_signal"]:
        # 计算正向信号数量（补偿信号）
        positive_score = 0
        if s3["has_positive_reciprocity"]:
            positive_score += 1
        if s2["response_length"] in ["中", "长"]:
            positive_score += 1
        if s2["interaction_reciprocity"] == "正向承接":
            positive_score += 1
        if s2["emotional_tone"] == "热":
            positive_score += 1
        if s2["topic_depth"] in ["中", "深"]:
            positive_score += 1
        if s3["has_intimacy_signal"]:
            positive_score += 1

        # 需要至少两个正向信号来补偿拒绝信号
        if positive_score < 2:
            return False

    # 检查是否有弱信号组合但缺少正向承接的情况
    # 若仅有以下信号但 response_length = "短" 且 interaction_reciprocity = "弱承接"
    # 且 has_positive_reciprocity = false，则兴趣等级应为"低"
    has_weak_signal_combination = (
        (s3["has_push_pull_pattern"] or s3["has_intimacy_signal"] or s3["has_relationship_probe"])
        and s2["response_length"] == "短"
        and s2["interaction_reciprocity"] == "弱承接"
        and not s3["has_positive_reciprocity"]
    )

    if has_weak_signal_combination:
        return False

    # 额外收紧：如果互动弱（短+弱承接）且情绪为温/无法判断，即使有required_signal也不给中
    # 除非有明确正向承接
    weak_interaction = (
        s2["response_length"] == "短"
        and s2["interaction_reciprocity"] == "弱承接"
        and s2["emotional_tone"] in ["温", "无法判断", ""]
    )
    if weak_interaction and not s3["has_positive_reciprocity"]:
        return False

    return True


# =========================
# interest_level
# =========================

def infer_interest_level(s2: Dict[str, Any], s3: Dict[str, Any], relationship_stage: str, debug_info: Optional[Dict[str, Any]] = None) -> str:
    if relationship_stage == "无法判断":
        if debug_info is not None:
            debug_info["interest_reason"] = "兴趣等级无法判断：关系阶段为无法判断"
        return "无法判断"

    if relationship_stage == "冷淡期":
        if debug_info is not None:
            debug_info["interest_reason"] = "兴趣等级低：关系阶段为冷淡期"
        return "低"

    if relationship_stage == "初识期":
        if _initial_medium_signal(s2, s3):
            if debug_info is not None:
                debug_info["interest_reason"] = "兴趣等级中：初识期但满足中兴趣信号条件"
            return "中"
        if debug_info is not None:
            debug_info["interest_reason"] = "兴趣等级低：初识期且不满足中兴趣信号条件"
        return "低"

    if relationship_stage == "暧昧期":
        if _ambiguous_high_signal(s2, s3, relationship_stage):
            if debug_info is not None:
                debug_info["interest_reason"] = "兴趣等级高：暧昧期且满足高兴趣信号条件"
            return "高"
        if debug_info is not None:
            debug_info["interest_reason"] = "兴趣等级中：暧昧期但不满足高兴趣信号条件"
        return "中"

    if relationship_stage == "拉扯期":
        if _pull_low_signal(s2, s3):
            if debug_info is not None:
                debug_info["interest_reason"] = "兴趣等级低：拉扯期且满足低兴趣信号条件"
            return "低"
        if _pull_medium_signal(s2, s3):
            if debug_info is not None:
                debug_info["interest_reason"] = "兴趣等级中：拉扯期且满足中兴趣信号条件"
            return "中"
        if debug_info is not None:
            debug_info["interest_reason"] = "兴趣等级低：拉扯期且不满足中兴趣信号条件"
        return "低"

    if debug_info is not None:
        debug_info["interest_reason"] = "兴趣等级低：默认返回低"
    return "低"


# =========================
# next_step_action
# =========================

def infer_next_step_action(
    s2: Dict[str, Any],
    s3: Dict[str, Any],
    relationship_stage: str,
    interest_level: str,
) -> str:
    """
    next_step 的规则决策层。
    这里只输出动作码，不输出自然语言长句。
    """

    if relationship_stage == "无法判断":
        if is_very_weak_s2(s2) or is_functional_minimal_interaction(s2, s3):
            return "observe"
        return "hold"

    if relationship_stage == "初识期":
        if interest_level == "中":
            if s2["interaction_reciprocity"] == "正向承接":
                return "light_extend"
            return "light_reply"
        return "light_reply"

    if relationship_stage == "暧昧期":
        # 明确双向靠近，顺势承接
        if (
            s3["has_intimacy_signal"]
            and s3["has_positive_reciprocity"]
            and not s3["has_rejection_signal"]
            and not s3["has_push_pull_pattern"]
            and not s3["has_sustained_coldness"]
        ):
            return "follow_reciprocity"

        # 其余暧昧期统一收敛到轻试探
        return "light_probe"

    if relationship_stage == "拉扯期":
        if s3["has_push_pull_pattern"]:
            return "step_back"

        if s3["has_rejection_signal"] or s2["emotional_tone"] == "冷":
            return "deescalate"

        return "step_back"

    if relationship_stage == "冷淡期":
        if s3["has_sustained_coldness"] or s3["has_rejection_signal"]:
            return "pause_contact"
        return "reduce_investment"

    return "observe"


NEXT_STEP_ACTION_TEXT = {
    "observe": "继续观察",
    "hold": "暂不加码",
    "light_reply": "轻度回应即可",
    "light_extend": "延续当前话题",
    "light_probe": "轻度试探反馈",
    "follow_reciprocity": "顺势承接互动",
    "deescalate": "降低互动频率",
    "step_back": "暂时后撤观察",
    "pause_contact": "暂停主动联系",
    "reduce_investment": "明确降低投入",
}


def map_next_step_action_to_text(action: str) -> str:
    return NEXT_STEP_ACTION_TEXT.get(_safe_str(action), "继续观察")


# =========================
# 对外统一入口
# =========================

def infer_r1(s2: Dict[str, Any] | None, s3: Dict[str, Any] | None) -> Dict[str, str]:
    s2n = _norm_s2(s2)
    s3n = _norm_s3(s3)

    relationship_stage = infer_relationship_stage(s2n, s3n)
    interest_level = infer_interest_level(s2n, s3n, relationship_stage)

    if relationship_stage == "无法判断":
        interest_level = "无法判断"

    next_step_action = infer_next_step_action(
        s2n, s3n, relationship_stage, interest_level
    )

    return {
        "relationship_stage": relationship_stage,
        "interest_level": interest_level,
        "next_step_action": next_step_action,
    }


def infer_r1_with_debug(s2: Dict[str, Any] | None, s3: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    推断R1结果并包含调试信息。

    返回的字典包含原始结果字段以及调试信息：
    - relationship_stage: 关系阶段
    - interest_level: 兴趣等级
    - next_step_action: 下一步动作
    - r1_debug_flags: 调试标志字典
    - r1_stage_reason: 阶段判断原因
    - r1_interest_reason: 兴趣等级判断原因
    """
    s2n = _norm_s2(s2)
    s3n = _norm_s3(s3)

    debug_info = {}

    # 收集调试信息
    relationship_stage = infer_relationship_stage(s2n, s3n, debug_info)
    interest_level = infer_interest_level(s2n, s3n, relationship_stage, debug_info)

    if relationship_stage == "无法判断":
        interest_level = "无法判断"

    next_step_action = infer_next_step_action(
        s2n, s3n, relationship_stage, interest_level
    )

    # 提取调试标志
    r1_debug_flags = {}
    flag_keys = ["has_any_advanced_signal", "is_very_weak_s2",
                 "is_functional_minimal_interaction", "is_judgable"]
    for key in flag_keys:
        if key in debug_info:
            r1_debug_flags[key] = debug_info[key]

    return {
        "relationship_stage": relationship_stage,
        "interest_level": interest_level,
        "next_step_action": next_step_action,
        "r1_debug_flags": r1_debug_flags,
        "r1_stage_reason": debug_info.get("stage_reason", "未知原因"),
        "r1_interest_reason": debug_info.get("interest_reason", "未知原因"),
    }