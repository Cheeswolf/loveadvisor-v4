# test_system/scripts/debug_a2_a3_root_cause.py
# -*- coding: utf-8 -*-
"""
专门用于追踪A2/A3根因的调试脚本。
目标：定位A2/A3在真实全链路批测中被低估为“低”的根本原因。
本轮只允许做链路追踪与原因定位，不允许修改任何业务代码。
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# =========================
# 强制把项目根目录放到 sys.path 最前面
# 防止导入到 site-packages 里的同名 app 包
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# 导入 pipeline_service，因为它已经导入了 coze_client
from app.services import pipeline_service
from app.services.result_parser import extract_nested_output
from app.rules.rules import infer_r1_with_debug, _initial_medium_signal
from configs.settings import EXTRACT_WORKFLOW_ID, S5_WORKFLOW_ID

# 从 pipeline_service 中获取 run_workflow
run_workflow = pipeline_service.run_workflow


def load_cases() -> list:
    """加载测试用例"""
    case_file = PROJECT_ROOT / "test_system" / "data" / "test_cases.json"
    with open(case_file, "r", encoding="utf-8") as f:
        return json.load(f)


def debug_initial_medium_signal(s2: Dict[str, Any], s3: Dict[str, Any]) -> Dict[str, Any]:
    """
    调试 _initial_medium_signal 函数，返回所有关键中间值。
    按照任务要求输出：
    - score、weak_interaction、negative flags、最终返回值
    """
    # 复制 _initial_medium_signal 的核心逻辑，但返回中间值
    debug_info = {}

    # 1. 负向信号检查
    has_negative_signal = (
        s3["has_rejection_signal"]
        or s2.get("emotional_tone") == "冷"
        or s2.get("interaction_reciprocity") == "明显回避"
        or s3["has_sustained_coldness"]
    )
    debug_info["has_negative_signal"] = has_negative_signal
    debug_info["negative_signal_details"] = {
        "has_rejection_signal": s3["has_rejection_signal"],
        "emotional_tone_is_cold": s2.get("emotional_tone") == "冷",
        "interaction_reciprocity_is_明显回避": s2.get("interaction_reciprocity") == "明显回避",
        "has_sustained_coldness": s3["has_sustained_coldness"]
    }

    if has_negative_signal:
        debug_info["final_result"] = False
        debug_info["blocked_by"] = "负向信号"
        return debug_info

    # 2. 互动强度检查
    weak_interaction = (
        s2.get("response_length") == "短"
        and s2.get("interaction_reciprocity") == "弱承接"
    )
    debug_info["weak_interaction"] = weak_interaction
    debug_info["weak_interaction_details"] = {
        "response_length": s2.get("response_length"),
        "interaction_reciprocity": s2.get("interaction_reciprocity"),
        "response_length_is_短": s2.get("response_length") == "短",
        "interaction_reciprocity_is_弱承接": s2.get("interaction_reciprocity") == "弱承接"
    }

    # 3. 正向信号计分
    score = 0
    score_details = {}

    if s3["has_relationship_probe"]:
        score += 1
        score_details["has_relationship_probe"] = True
    else:
        score_details["has_relationship_probe"] = False

    if s3["has_positive_reciprocity"]:
        score += 1
        score_details["has_positive_reciprocity"] = True
    else:
        score_details["has_positive_reciprocity"] = False

    if s2.get("emotional_tone") == "热":
        score += 1
        score_details["emotional_tone_is_热"] = True
    else:
        score_details["emotional_tone_is_热"] = False

    if s2.get("topic_depth") in ["中", "深"]:
        score += 1
        score_details["topic_depth_is_中或深"] = True
    else:
        score_details["topic_depth_is_中或深"] = False

    if s2.get("interaction_reciprocity") == "正向承接":
        score += 1
        score_details["interaction_reciprocity_is_正向承接"] = True
    else:
        score_details["interaction_reciprocity_is_正向承接"] = False

    debug_info["score"] = score
    debug_info["score_details"] = score_details

    # 基础要求：至少两个正向信号
    if score < 2:
        debug_info["final_result"] = False
        debug_info["blocked_by"] = "正向信号不足 (score < 2)"
        return debug_info

    # 4. 弱互动补偿检查
    if weak_interaction and not s3["has_positive_reciprocity"] and s2.get("interaction_reciprocity") != "正向承接":
        debug_info["final_result"] = False
        debug_info["blocked_by"] = "弱互动且无正向承接补偿"
        return debug_info

    debug_info["final_result"] = True
    return debug_info


def main():
    """主函数"""
    cases = load_cases()
    target_ids = {"A2", "A3"}
    matched = [case for case in cases if case.get("sample_id") in target_ids]

    if not matched:
        print(f"未找到目标样本: {target_ids}")
        return

    all_results = []
    for case in matched:
        sample_id = case.get("sample_id", "UNKNOWN")
        text = case.get("input_text", "")

        print("\n" + "=" * 80)
        print(f"DEBUG CASE: {sample_id}")
        print("=" * 80)
        print("原始输入文本:")
        print(text)
        print("=" * 80)

        # 调用前半段工作流（S1/S2/S3）
        extract_data = run_workflow(
            EXTRACT_WORKFLOW_ID,
            {
                "chat_text": text
            }
        )

        s2 = extract_nested_output(extract_data, "S2_output")
        s3 = extract_nested_output(extract_data, "S3_output")

        print("\n=== EXTRACTED S2 ===")
        print(json.dumps(s2, ensure_ascii=False, indent=2))
        print("\n=== EXTRACTED S3 ===")
        print(json.dumps(s3, ensure_ascii=False, indent=2))

        # 调用 R1 规则引擎（带调试信息）
        r1_result = infer_r1_with_debug(s2, s3)

        print("\n=== R1 RESULT WITH DEBUG ===")
        print(json.dumps(r1_result, ensure_ascii=False, indent=2))

        # 调试 _initial_medium_signal
        print("\n=== DEBUG _initial_medium_signal ===")
        medium_signal_debug = debug_initial_medium_signal(s2, s3)
        print(json.dumps(medium_signal_debug, ensure_ascii=False, indent=2))

        # 组装结果
        result = {
            "sample_id": sample_id,
            "input_text": text,
            "s2": s2,
            "s3": s3,
            "relationship_stage": r1_result["relationship_stage"],
            "interest_level": r1_result["interest_level"],
            "r1_debug_flags": r1_result["r1_debug_flags"],
            "r1_stage_reason": r1_result["r1_stage_reason"],
            "r1_interest_reason": r1_result["r1_interest_reason"],
            "_initial_medium_signal_debug": medium_signal_debug,
        }
        all_results.append(result)

        print("\n" + "=" * 80)
        print(f"SUMMARY FOR {sample_id}:")
        print(f"  Relationship Stage: {r1_result['relationship_stage']}")
        print(f"  Interest Level: {r1_result['interest_level']}")
        print(f"  Stage Reason: {r1_result['r1_stage_reason']}")
        print(f"  Interest Reason: {r1_result['r1_interest_reason']}")
        print(f"  Debug Flags: {r1_result['r1_debug_flags']}")
        print(f"  _initial_medium_signal result: {medium_signal_debug.get('final_result', 'N/A')}")
        if "blocked_by" in medium_signal_debug:
            print(f"  Blocked by: {medium_signal_debug['blocked_by']}")
        print("=" * 80)

    # 根因分析
    print("\n\n" + "=" * 100)
    print("A2/A3 根因分析")
    print("=" * 100)

    for res in all_results:
        sample_id = res["sample_id"]
        expected_interest = None
        # 从原始用例中获取预期兴趣等级
        for case in cases:
            if case["sample_id"] == sample_id:
                expected_interest = case["expected_interest_level"]
                break

        actual_interest = res["interest_level"]
        medium_debug = res["_initial_medium_signal_debug"]

        print(f"\n{sample_id}:")
        print(f"  预期兴趣等级: {expected_interest}")
        print(f"  实际兴趣等级: {actual_interest}")
        print(f"  关系阶段: {res['relationship_stage']}")

        # 判断根因层次
        print(f"\n  根因分析:")

        # 1. 检查 S2 信号提取
        s2 = res["s2"]
        print(f"  - S2 信号:")
        print(f"    主动性: {s2.get('initiative')}")
        print(f"    回应长度: {s2.get('response_length')}")
        print(f"    情感基调: {s2.get('emotional_tone')}")
        print(f"    话题深度: {s2.get('topic_depth')}")
        print(f"    互动承接性: {s2.get('interaction_reciprocity')}")
        print(f"    关键信号: {s2.get('key_signals', [])}")

        # 2. 检查 S3 信号提取
        s3 = res["s3"]
        print(f"  - S3 信号:")
        print(f"    亲密信号: {s3.get('has_intimacy_signal')}")
        print(f"    关系试探: {s3.get('has_relationship_probe')}")
        print(f"    正向承接: {s3.get('has_positive_reciprocity')}")
        print(f"    拒绝信号: {s3.get('has_rejection_signal')}")
        print(f"    推拉模式: {s3.get('has_push_pull_pattern')}")
        print(f"    持续冷淡: {s3.get('has_sustained_coldness')}")
        print(f"    信号摘要: {s3.get('signal_summary', [])}")

        # 3. 检查 stage 判定
        print(f"  - Stage 判定: {res['r1_stage_reason']}")

        # 4. 检查 interest 规则 (_initial_medium_signal)
        print(f"  - Interest 规则 (_initial_medium_signal):")
        print(f"    最终结果: {medium_debug.get('final_result')}")
        if "blocked_by" in medium_debug:
            print(f"    被阻止原因: {medium_debug['blocked_by']}")
        print(f"    负向信号: {medium_debug.get('has_negative_signal')}")
        print(f"    弱互动: {medium_debug.get('weak_interaction')}")
        print(f"    得分: {medium_debug.get('score')}")

        # 5. 判断根本原因属于哪一层
        print(f"\n  根本原因定位:")
        if not medium_debug.get('final_result', False):
            # _initial_medium_signal 返回 False
            if medium_debug.get('has_negative_signal', False):
                print(f"    → 属于: interest 规则层 (负向信号阻止)")
            elif medium_debug.get('score', 0) < 2:
                print(f"    → 属于: interest 规则层 (正向信号不足)")
            elif medium_debug.get('weak_interaction', False) and medium_debug.get('blocked_by', '').startswith('弱互动'):
                print(f"    → 属于: interest 规则层 (弱互动且无补偿)")
            else:
                print(f"    → 属于: interest 规则层 (其他原因)")
        else:
            # _initial_medium_signal 返回 True，但兴趣等级仍为低？
            # 这不应该发生，但检查一下
            if actual_interest == "低":
                print(f"    → 异常: _initial_medium_signal 返回 True，但兴趣等级为低")
                print(f"    → 可能属于: 其他层")
            else:
                print(f"    → 属于: interest 规则层 (通过)")

        # 6. 下一步最应该修改的位置
        print(f"\n  下一步最应该修改的位置:")
        if not medium_debug.get('final_result', False):
            if medium_debug.get('has_negative_signal', False):
                print(f"    → 修改: _initial_medium_signal 中的负向信号检查逻辑")
            elif medium_debug.get('score', 0) < 2:
                print(f"    → 修改: _initial_medium_signal 中的计分规则或阈值")
            elif medium_debug.get('weak_interaction', False):
                print(f"    → 修改: _initial_medium_signal 中的弱互动补偿条件")
            else:
                print(f"    → 修改: _initial_medium_signal 函数")
        else:
            print(f"    → 异常: _initial_medium_signal 通过但兴趣等级仍为低，需要进一步调试")

        print(f"  - 未完成项: 需要根据具体信号值确定精确的修改方案")

    # 保存详细结果到文件
    output_file = PROJECT_ROOT / "test_system" / "output" / "a2_a3_root_cause_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n详细分析结果已保存到: {output_file}")


if __name__ == "__main__":
    main()