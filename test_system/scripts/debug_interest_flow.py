# test_system/scripts/debug_interest_flow.py
# -*- coding: utf-8 -*-
"""
专门追踪 A2/A3 样本中 interest_level 值传递链路。
目标：定位 interest_level 从“中”变成“低”的具体代码路径。
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# 强制把项目根目录放到 sys.path 最前面
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.rules.rules import (
    _norm_s2, _norm_s3,
    infer_relationship_stage,
    infer_interest_level,
    infer_r1,
    infer_r1_with_debug,
    _initial_medium_signal,
    _ambiguous_high_signal,
    _pull_low_signal,
    _pull_medium_signal
)
# from app.services.output_builder.v2 import assemble_output
# from app.services.pipeline_service import run_pipeline


def load_cases() -> list:
    """加载测试用例"""
    case_file = PROJECT_ROOT / "test_system" / "data" / "test_cases.json"
    with open(case_file, "r", encoding="utf-8") as f:
        return json.load(f)


def trace_interest_flow(s2: Dict[str, Any], s3: Dict[str, Any], sample_id: str):
    """追踪 interest_level 在每一层的实际值"""
    print(f"\n{'='*80}")
    print(f"TRACING INTEREST FLOW FOR {sample_id}")
    print(f"{'='*80}")

    # 1. 规范化 S2, S3
    s2n = _norm_s2(s2)
    s3n = _norm_s3(s3)
    print("Normalized S2:", json.dumps(s2n, ensure_ascii=False, indent=2))
    print("Normalized S3:", json.dumps(s3n, ensure_ascii=False, indent=2))

    # 2. 调用 _initial_medium_signal 直接检查
    medium_result = _initial_medium_signal(s2n, s3n)
    print(f"\n[1] _initial_medium_signal direct call result: {medium_result}")

    # 3. infer_relationship_stage
    stage_debug = {}
    relationship_stage = infer_relationship_stage(s2n, s3n, stage_debug)
    print(f"\n[2] infer_relationship_stage result: {relationship_stage}")
    print(f"    stage_debug: {json.dumps(stage_debug, ensure_ascii=False, indent=2)}")

    # 4. infer_interest_level 带调试
    interest_debug = {}
    interest_level = infer_interest_level(s2n, s3n, relationship_stage, interest_debug)
    print(f"\n[3] infer_interest_level result: {interest_level}")
    print(f"    interest_debug: {json.dumps(interest_debug, ensure_ascii=False, indent=2)}")

    # 5. infer_r1 (不带调试)
    r1_result = infer_r1(s2, s3)  # 注意：这里传入原始 s2, s3，函数内部会规范化
    print(f"\n[4] infer_r1 result: {json.dumps(r1_result, ensure_ascii=False, indent=2)}")

    # 6. infer_r1_with_debug
    r1_debug_result = infer_r1_with_debug(s2, s3)
    print(f"\n[5] infer_r1_with_debug result: {json.dumps(r1_debug_result, ensure_ascii=False, indent=2)}")

    # 7. 检查是否有不一致
    if interest_level != r1_result.get("interest_level"):
        print(f"\n[WARNING] infer_interest_level 返回 '{interest_level}'，但 infer_r1 返回 '{r1_result.get('interest_level')}'")

    if r1_result.get("interest_level") != r1_debug_result.get("interest_level"):
        print(f"\n[WARNING] infer_r1 和 infer_r1_with_debug 的 interest_level 不一致")

    # 8. 模拟 pipeline 输出 (不实际调用工作流) - 跳过，因为不需要
    print(f"\n[6] assemble_output skipped (requires import)")

    # 9. 实际调用 pipeline (可选，但可能耗时) - 跳过
    # print(f"\n[7] Actual pipeline output skipped (requires import)")

    return {
        "sample_id": sample_id,
        "_initial_medium_signal": medium_result,
        "relationship_stage": relationship_stage,
        "infer_interest_level_result": interest_level,
        "infer_r1_interest_level": r1_result.get("interest_level"),
        "infer_r1_with_debug_interest_level": r1_debug_result.get("interest_level"),
        "interest_reason": interest_debug.get("interest_reason"),
        "stage_reason": stage_debug.get("stage_reason"),
        "r1_debug_flags": r1_debug_result.get("r1_debug_flags"),
    }


def main():
    cases = load_cases()
    target_ids = {"A2", "A3"}
    matched = [case for case in cases if case.get("sample_id") in target_ids]

    if not matched:
        print(f"未找到目标样本: {target_ids}")
        return

    # 使用已有的 debug 输出中的 S2/S3 数据，避免重复调用工作流
    debug_file = PROJECT_ROOT / "test_system" / "output" / "a2_a3_debug_output.json"
    if debug_file.exists():
        with open(debug_file, "r", encoding="utf-8") as f:
            debug_data = json.load(f)
    else:
        debug_data = {}

    all_traces = []
    for case in matched:
        sample_id = case.get("sample_id")
        print(f"\n{'#'*80}")
        print(f"Processing {sample_id}")
        print(f"{'#'*80}")

        # 如果已有 debug 数据，直接使用
        if sample_id in debug_data:
            s2 = debug_data[sample_id]["debug"]["s2"]
            s3 = debug_data[sample_id]["debug"]["s3"]
            print("Using cached S2/S3 from debug output")
        else:
            # 否则需要运行工作流（暂不实现）
            print("No cached data, skipping (would need to run workflow)")
            continue

        trace = trace_interest_flow(s2, s3, sample_id)
        all_traces.append(trace)

    # 汇总分析
    print(f"\n{'='*100}")
    print("VALUE FLOW TRACING SUMMARY")
    print(f"{'='*100}")

    for trace in all_traces:
        print(f"\n[{trace['sample_id']}]")
        print(f"  _initial_medium_signal: {trace['_initial_medium_signal']}")
        print(f"  relationship_stage: {trace['relationship_stage']}")
        print(f"  infer_interest_level result: {trace['infer_interest_level_result']}")
        print(f"  infer_r1 interest_level: {trace['infer_r1_interest_level']}")
        print(f"  infer_r1_with_debug interest_level: {trace['infer_r1_with_debug_interest_level']}")
        print(f"  interest_reason: {trace['interest_reason']}")
        print(f"  stage_reason: {trace['stage_reason']}")

        # 判断问题点
        if trace['_initial_medium_signal'] == True and trace['infer_interest_level_result'] == "低":
            print(f"  → PROBLEM: _initial_medium_signal 返回 True，但 infer_interest_level 返回 '低'")
            print(f"    需要检查 infer_interest_level 函数中 relationship_stage 是否为 '初识期'")
            print(f"    当前 relationship_stage: {trace['relationship_stage']}")

        if trace['infer_interest_level_result'] != trace['infer_r1_interest_level']:
            print(f"  → PROBLEM: infer_interest_level 与 infer_r1 结果不一致")

        if trace['infer_r1_interest_level'] != trace['infer_r1_with_debug_interest_level']:
            print(f"  → PROBLEM: infer_r1 与 infer_r1_with_debug 结果不一致")

    # 保存追踪结果
    output_file = PROJECT_ROOT / "test_system" / "output" / "interest_flow_trace.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_traces, f, ensure_ascii=False, indent=2)
    print(f"\n详细追踪结果已保存到: {output_file}")


if __name__ == "__main__":
    main()