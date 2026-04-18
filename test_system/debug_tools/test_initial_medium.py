#!/usr/bin/env python3
# 测试 _initial_medium_signal 逻辑

def _initial_medium_signal(s2, s3):
    """初识期给中"""
    # 负向信号检查
    has_negative_signal = (
        s3["has_rejection_signal"]
        or s2["emotional_tone"] == "冷"
        or s2["interaction_reciprocity"] == "明显回避"
        or s3["has_sustained_coldness"]
    )
    if has_negative_signal:
        print("has_negative_signal true")
        return False

    # 互动强度检查
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

    print(f"score: {score}, weak_interaction: {weak_interaction}")
    print(f"has_positive_reciprocity: {s3['has_positive_reciprocity']}")
    print(f"interaction_reciprocity: {s2['interaction_reciprocity']}")

    # 基础要求：至少两个正向信号
    if score < 2:
        print("score < 2")
        return False

    # 如果互动弱且没有正向承接，即使有两个正向信号也不给中
    if weak_interaction and not s3["has_positive_reciprocity"] and s2["interaction_reciprocity"] != "正向承接":
        print("weak_interaction without positive_reciprocity or正向承接")
        return False

    print("All conditions passed, returning True")
    return True

# A2 数据
s2_a2 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接"
}

s3_a2 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": True,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False
}

print("=== Testing A2 ===")
result_a2 = _initial_medium_signal(s2_a2, s3_a2)
print(f"Result: {result_a2}")

# A3 数据
s2_a3 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接"
}

s3_a3 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": True,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False
}

print("\n=== Testing A3 ===")
result_a3 = _initial_medium_signal(s2_a3, s3_a3)
print(f"Result: {result_a3}")