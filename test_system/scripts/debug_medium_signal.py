import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.rules.rules import _norm_s2, _norm_s3

debug_file = PROJECT_ROOT / "test_system" / "output" / "a2_a3_debug_output.json"
with open(debug_file, 'r', encoding='utf-8') as f:
    debug_data = json.load(f)

def debug_initial_medium_signal(s2, s3):
    """复制 _initial_medium_signal 逻辑并打印每一步"""
    print("=== DEBUG _initial_medium_signal ===")
    print(f"s2: {json.dumps(s2, ensure_ascii=False, indent=2)}")
    print(f"s3: {json.dumps(s3, ensure_ascii=False, indent=2)}")

    # 负向信号检查
    has_negative_signal = (
        s3["has_rejection_signal"]
        or s2["emotional_tone"] == "冷"
        or s2["interaction_reciprocity"] == "明显回避"
        or s3["has_sustained_coldness"]
    )
    print(f"1. has_negative_signal: {has_negative_signal}")
    print(f"   details: rejection={s3['has_rejection_signal']}, emotional_tone cold={s2['emotional_tone'] == '冷'}, reciprocity 明显回避={s2['interaction_reciprocity'] == '明显回避'}, sustained_coldness={s3['has_sustained_coldness']}")
    if has_negative_signal:
        print("   -> RETURN False (负向信号)")
        return False

    # 互动强度检查
    weak_interaction = (
        s2["response_length"] == "短"
        and s2["interaction_reciprocity"] == "弱承接"
    )
    print(f"2. weak_interaction: {weak_interaction}")
    print(f"   details: response_length='{s2['response_length']}' == '短'? {s2['response_length'] == '短'}, reciprocity='{s2['interaction_reciprocity']}' == '弱承接'? {s2['interaction_reciprocity'] == '弱承接'}")

    # 正向信号计分
    score = 0
    if s3["has_relationship_probe"]:
        score += 1
    if s3["has_positive_reciprocity"]:
        score += 2  # 注意：原函数中正向互惠计2分
    if s2["emotional_tone"] == "热":
        score += 1
    if s2["topic_depth"] in ["中", "深"]:
        score += 1
    if s2["interaction_reciprocity"] == "正向承接":
        score += 1
    print(f"3. score: {score}")
    print(f"   details: relationship_probe={s3['has_relationship_probe']}, positive_reciprocity={s3['has_positive_reciprocity']} (+2), emotional_tone hot={s2['emotional_tone'] == '热'}, topic_depth in [中,深]={s2['topic_depth'] in ['中','深']}, reciprocity 正向承接={s2['interaction_reciprocity'] == '正向承接'}")

    # 基础要求：至少两个正向信号
    if score < 2:
        print(f"   -> RETURN False (score < 2)")
        return False
    print(f"   score >= 2 passed")

    # 最小补偿分支：弱互动但有真实正向互惠的边界样本（A2/A3修复）
    if weak_interaction and s3["has_positive_reciprocity"]:
        print(f"4. weak_interaction and has_positive_reciprocity: True -> RETURN True (A2/A3修复)")
        return True

    # 如果互动弱且没有正向承接，即使有两个正向信号也不给中
    if weak_interaction and not s3["has_positive_reciprocity"] and s2["interaction_reciprocity"] != "正向承接":
        print(f"5. weak_interaction and no positive_reciprocity and no 正向承接 -> RETURN False")
        return False

    print(f"6. All checks passed -> RETURN True")
    return True

for sample_id in ["A2", "A3"]:
    print(f"\n{'#'*80}")
    print(f"Sample {sample_id}")
    print(f"{'#'*80}")
    data = debug_data[sample_id]
    s2 = data["debug"]["s2"]
    s3 = data["debug"]["s3"]
    s2n = _norm_s2(s2)
    s3n = _norm_s3(s3)
    result = debug_initial_medium_signal(s2n, s3n)
    print(f"\nFinal result: {result}")

    # 调用原始函数比较
    from app.rules.rules import _initial_medium_signal
    original_result = _initial_medium_signal(s2n, s3n)
    print(f"Original function result: {original_result}")
    if result != original_result:
        print("*** MISMATCH ***")