# test_system/scripts/debug_phase8_2_9_pipeline.py
# -*- coding: utf-8 -*-

import json
import sys
from pathlib import Path

# =========================
# 强制把项目根目录放到 sys.path 最前面
# 防止导入到 site-packages 里的同名 app 包
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# 导入 pipeline_service，因为它已经导入了 coze_client
from app.services import pipeline_service
from app.services.result_parser import extract_nested_output
from app.rules.rules import infer_r1_with_debug
from configs.settings import EXTRACT_WORKFLOW_ID, S5_WORKFLOW_ID

# 从 pipeline_service 中获取 run_workflow
run_workflow = pipeline_service.run_workflow


def load_cases() -> list:
    case_file = PROJECT_ROOT / "test_system" / "data" / "test_cases.json"
    with open(case_file, "r", encoding="utf-8") as f:
        return json.load(f)


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

        print("\n" + "=" * 80)
        print(f"DEBUG CASE: {sample_id}")
        print("=" * 80)
        print("INPUT TEXT:")
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
        }
        all_results.append(result)

        print("\n" + "=" * 80)
        print(f"SUMMARY FOR {sample_id}:")
        print(f"  Relationship Stage: {r1_result['relationship_stage']}")
        print(f"  Interest Level: {r1_result['interest_level']}")
        print(f"  Stage Reason: {r1_result['r1_stage_reason']}")
        print(f"  Interest Reason: {r1_result['r1_interest_reason']}")
        print(f"  Debug Flags: {r1_result['r1_debug_flags']}")
        print("=" * 80)

    # 汇总对比表
    print("\n\n" + "=" * 100)
    print("SUMMARY COMPARISON TABLE")
    print("=" * 100)
    headers = ["Sample", "Relationship Stage", "Interest Level", "Stage Reason", "Interest Reason", "Debug Flags"]
    print(f"{headers[0]:<6} | {headers[1]:<15} | {headers[2]:<15} | {headers[3]:<40} | {headers[4]:<40} | {headers[5]}")
    print("-" * 150)
    for res in all_results:
        flags_str = json.dumps(res["r1_debug_flags"], ensure_ascii=False)
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