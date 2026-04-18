#!/usr/bin/env python3
"""
快速验证 E3 和 C1 修复效果。
直接调用规则函数，模拟 S2/S3 数据。
"""
import sys
sys.path.insert(0, '.')

from app.rules.rules import infer_r1_with_debug, is_low_quality_key_signals

def test_e3():
    print("=== Testing E3 fix ===")
    # 模拟 E3 的 S2/S3 数据
    s2 = {
        "initiative": "无法判断",
        "response_length": "短",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": ["简短回应", "未推进"]
    }
    s3 = {
        "has_intimacy_signal": False,
        "has_relationship_probe": False,
        "has_positive_reciprocity": False,
        "has_rejection_signal": False,
        "has_push_pull_pattern": False,
        "has_sustained_coldness": False,
        "signal_summary": []
    }

    # 测试 is_low_quality_key_signals
    key_signals = s2["key_signals"]
    print(f"key_signals: {key_signals}")
    print(f"is_low_quality_key_signals: {is_low_quality_key_signals(key_signals)}")

    # 测试 infer_r1_with_debug
    result = infer_r1_with_debug(s2, s3)
    print(f"relationship_stage: {result['relationship_stage']} (expected: 无法判断)")
    print(f"interest_level: {result['interest_level']} (expected: 无法判断)")
    print(f"debug flags: {result['r1_debug_flags']}")
    print(f"stage reason: {result['r1_stage_reason']}")

    assert result['relationship_stage'] == "无法判断", f"E3 should be 无法判断, got {result['relationship_stage']}"
    assert result['interest_level'] == "无法判断", f"E3 interest should be 无法判断, got {result['interest_level']}"
    print("PASS: E3 fix passed\n")

def test_c1():
    print("=== Testing C1 fix ===")
    # 模拟 C1 的 S2/S3 数据（冲突型拉扯）
    s2 = {
        "initiative": "A更主动",
        "response_length": "短",  # 可能短
        "emotional_tone": "冷",
        "topic_depth": "浅",
        "interaction_reciprocity": "明显回避",
        "key_signals": ["关系变化", "回避解释"]  # 包含关系上下文
    }
    s3 = {
        "has_intimacy_signal": False,
        "has_relationship_probe": True,  # 可能有关系试探
        "has_positive_reciprocity": False,  # 无正向承接
        "has_rejection_signal": True,  # 有拒绝信号
        "has_push_pull_pattern": False,
        "has_sustained_coldness": False,
        "signal_summary": ["关系追问", "回避"]
    }

    result = infer_r1_with_debug(s2, s3)
    print(f"relationship_stage: {result['relationship_stage']} (expected: 拉扯期)")
    print(f"interest_level: {result['interest_level']} (expected: 中)")
    print(f"debug flags: {result['r1_debug_flags']}")
    print(f"stage reason: {result['r1_stage_reason']}")
    print(f"interest reason: {result['r1_interest_reason']}")

    # 期望：拉扯期，中兴趣
    assert result['relationship_stage'] == "拉扯期", f"C1 stage should be 拉扯期, got {result['relationship_stage']}"
    assert result['interest_level'] == "中", f"C1 interest should be 中, got {result['interest_level']}"
    print("PASS: C1 fix passed\n")

def test_other_groups():
    """确保 A/B/D 组不受影响"""
    print("=== Testing other groups (A/B/D) ===")

    # A1 样本
    s2_a1 = {
        "initiative": "双方接近",
        "response_length": "中",
        "emotional_tone": "温",
        "topic_depth": "浅",
        "interaction_reciprocity": "弱承接",
        "key_signals": ["互相问候", "询问专业"]
    }
    s3_a1 = {
        "has_intimacy_signal": False,
        "has_relationship_probe": False,
        "has_positive_reciprocity": False,
        "has_rejection_signal": False,
        "has_push_pull_pattern": False,
        "has_sustained_coldness": False,
        "signal_summary": ["基础互动"]
    }

    result_a1 = infer_r1_with_debug(s2_a1, s3_a1)
    print(f"A1: stage={result_a1['relationship_stage']}, interest={result_a1['interest_level']}")
    assert result_a1['relationship_stage'] == "初识期", "A1 should be 初识期"
    assert result_a1['interest_level'] == "低", "A1 interest should be 低"

    # B1 样本（暧昧期高兴趣）
    s2_b1 = {
        "initiative": "双方接近",
        "response_length": "中",
        "emotional_tone": "热",
        "topic_depth": "中",
        "interaction_reciprocity": "正向承接",
        "key_signals": ["表达想念", "暧昧回应"]
    }
    s3_b1 = {
        "has_intimacy_signal": True,
        "has_relationship_probe": True,
        "has_positive_reciprocity": True,
        "has_rejection_signal": False,
        "has_push_pull_pattern": False,
        "has_sustained_coldness": False,
        "signal_summary": ["亲密信号"]
    }

    result_b1 = infer_r1_with_debug(s2_b1, s3_b1)
    print(f"B1: stage={result_b1['relationship_stage']}, interest={result_b1['interest_level']}")
    assert result_b1['relationship_stage'] == "暧昧期", "B1 should be 暧昧期"
    # 兴趣可能是中或高，取决于条件，我们不严格断言

    print("PASS: Other groups unaffected\n")

if __name__ == "__main__":
    try:
        test_e3()
        test_c1()
        test_other_groups()
        print("SUCCESS: All tests passed!")
    except AssertionError as e:
        print(f"FAIL: Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)