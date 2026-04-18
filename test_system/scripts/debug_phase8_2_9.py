# test_system/scripts/debug_phase8_2_9.py
# -*- coding: utf-8 -*-
"""
V3-Phase8.2.9-C组与E组真实命中路径复盘
抓取 C1/C3/E2/E3 四个样本的真实 debug 命中路径，定位当前 R1 边界耦合问题。
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# =========================
# 强制把项目根目录放到 sys.path 最前面
# 防止导入到 site-packages 里的同名 app 包
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.coze_client import run_workflow
from app.services.result_parser import extract_nested_output
from app.rules.rules import infer_r1_with_debug
from configs.settings import EXTRACT_WORKFLOW_ID, S5_WORKFLOW_ID


def load_cases() -> list:
    case_file = PROJECT_ROOT / "test_system" / "data" / "test_cases.json"
    with open(case_file, "r", encoding="utf-8") as f:
        return json.load(f)


def run_sample(sample_id: str, input_text: str) -> Dict[str, Any]:
    """
    运行单个样本，返回包含所有调试信息的字典。
    """
    print("\n" + "=" * 80)
    print(f"DEBUG SAMPLE: {sample_id}")
    print("=" * 80)
    print("INPUT TEXT:")
    print(input_text)
    print("=" * 80)

    # Step 1: 调用前半段工作流（S1/S2/S3）
    print("\n[Step 1] Calling EXTRACT workflow...")
    extract_data = run_workflow(
        EXTRACT_WORKFLOW_ID,
        {
            "chat_text": input_text
        }
    )

    s2 = extract_nested_output(extract_data, "S2_output")
    s3 = extract_nested_output(extract_data, "S3_output")

    print(f"\n[Step 1] S2 extracted: {json.dumps(s2, ensure_ascii=False, indent=2)}")
    print(f"\n[Step 1] S3 extracted: {json.dumps(s3, ensure_ascii=False, indent=2)}")

    # Step 2: 调用 R1 规则引擎（带调试信息）
    print("\n[Step 2] Calling R1 inference with debug...")
    r1_result = infer_r1_with_debug(s2, s3)

    # Step 3: 可选调用 S5 工作流（为了完整性，但本轮复盘不需要）
    # 如果需要，可以取消注释
    # print("\n[Step 3] Calling S5 workflow...")
    # s5_data = run_workflow(
    #     S5_WORKFLOW_ID,
    #     {
    #         "S2_output": json.dumps(s2, ensure_ascii=False),
    #         "S3_output": json.dumps(s3, ensure_ascii=False),
    #         "R1_output": json.dumps(r1_result, ensure_ascii=False),
    #         "user_question": ""
    #     }
    # )
    # s5 = extract_nested_output(s5_data, "S5_output")
    # print(f"\n[Step 3] S5 extracted: {json.dumps(s5, ensure_ascii=False, indent=2)}")

    # 组装最终结果
    result = {
        "sample_id": sample_id,
        "input_text": input_text,
        "s2": s2,
        "s3": s3,
        "relationship_stage": r1_result["relationship_stage"],
        "interest_level": r1_result["interest_level"],
        "r1_debug_flags": r1_result["r1_debug_flags"],
        "r1_stage_reason": r1_result["r1_stage_reason"],
        "r1_interest_reason": r1_result["r1_interest_reason"],
        # "s5": s5,  # 可选
    }

    print("\n" + "=" * 80)
    print(f"RESULT FOR {sample_id}:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 80)

    return result


def main():
    cases = load_cases()
    target_ids = {"C1", "C3", "E2", "E3"}
    matched = [case for case in cases if case.get("sample_id") in target_ids]

    if not matched:
        print(f"未找到目标样本: {target_ids}")
        return

    all_results = []
    for case in matched:
        sample_id = case.get("sample_id", "UNKNOWN")
        text = case.get("input_text", "")
        result = run_sample(sample_id, text)
        all_results.append(result)

    # 汇总对比表
    print("\n\n" + "=" * 100)
    print("SUMMARY COMPARISON TABLE")
    print("=" * 100)
    headers = ["Sample", "Relationship Stage", "Interest Level", "Stage Reason", "Interest Reason", "Debug Flags"]
    print(f"{headers[0]:<6} | {headers[1]:<15} | {headers[2]:<15} | {headers[3]:<40} | {headers[4]:<40} | {headers[5]}")
    print("-" * 150)
    for res in all_results:
        flags_str = json.dumps(res["r1_debug_flags"], ensure_ascii=False)
        # 截断过长的字符串
        stage_reason = (res["r1_stage_reason"][:37] + "...") if len(res["r1_stage_reason"]) > 40 else res["r1_stage_reason"]
        interest_reason = (res["r1_interest_reason"][:37] + "...") if len(res["r1_interest_reason"]) > 40 else res["r1_interest_reason"]
        print(f"{res['sample_id']:<6} | {res['relationship_stage']:<15} | {res['interest_level']:<15} | {stage_reason:<40} | {interest_reason:<40} | {flags_str}")

    print("\n\n" + "=" * 100)
    print("ANALYSIS OF MISJUDGMENTS")
    print("=" * 100)

    # 根据结果分析误判原因
    for res in all_results:
        sample_id = res["sample_id"]
        expected_stage = None
        # 从原始用例中获取预期阶段
        for case in cases:
            if case["sample_id"] == sample_id:
                expected_stage = case["expected_relationship_stage"]
                break

        actual_stage = res["relationship_stage"]
        if expected_stage and actual_stage != expected_stage:
            print(f"\n{sample_id}: Expected '{expected_stage}', got '{actual_stage}'")
            print(f"  Stage reason: {res['r1_stage_reason']}")
            print(f"  Debug flags: {res['r1_debug_flags']}")
            print(f"  S2 summary: initiative={res['s2'].get('initiative')}, response_length={res['s2'].get('response_length')}, emotional_tone={res['s2'].get('emotional_tone')}, topic_depth={res['s2'].get('topic_depth')}, interaction_reciprocity={res['s2'].get('interaction_reciprocity')}")
            print(f"  S3 signals: {res['s3']}")
        else:
            print(f"\n{sample_id}: Correctly judged as '{actual_stage}'")

    print("\n" + "=" * 100)
    print("NEXT-ROUND SUGGESTED MODIFICATIONS (NOT TO IMPLEMENT NOW)")
    print("=" * 100)
    print("Based on the debug outputs above, suggest potential fixes for the misjudgments.")
    print("This is for planning purposes only - do not modify rules.py in this round.")


if __name__ == "__main__":
    main()