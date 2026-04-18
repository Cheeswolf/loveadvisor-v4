#!/usr/bin/env python3
"""
独立脚本，直接调用 Coze API 并应用 rules 逻辑，避免循环导入。
"""
import json
import sys
import requests
from pathlib import Path

# 从 configs/settings.py 中提取配置（硬编码）
COZE_API = "https://api.coze.cn/v1/workflow/run"
TOKEN = "pat_QUELD2jsDVTLlMntEAOCuqSXNyUGx1U4Eeh8Sg1jxpV8Qhg4rBQUuSetowoUOwz7"
EXTRACT_WORKFLOW_ID = "7623810752218497034"
S5_WORKFLOW_ID = "7624197219024994330"
REQUEST_TIMEOUT = 90

def run_workflow(workflow_id: str, parameters: dict) -> dict:
    """直接调用 Coze Workflow"""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "workflow_id": workflow_id,
        "parameters": parameters,
    }
    resp = requests.post(COZE_API, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    raw = resp.json()
    # 简化提取逻辑
    candidates = [
        raw.get("data"),
        raw.get("output"),
        raw.get("outputs"),
    ]
    if isinstance(raw.get("data"), dict):
        data_obj = raw["data"]
        candidates.extend([
            data_obj.get("output"),
            data_obj.get("outputs"),
            data_obj.get("result"),
        ])
    for item in candidates:
        if item is None:
            continue
        if isinstance(item, dict):
            return item
        if isinstance(item, list):
            return {"raw_list": item}
        if isinstance(item, str):
            try:
                parsed = json.loads(item)
                if isinstance(parsed, dict):
                    return parsed
            except:
                pass
            return {"raw_data": item}
    return {"_debug_error": "No usable output found in Coze response"}

def extract_nested_output(data: dict, key: str) -> dict:
    """提取嵌套输出"""
    if key in data:
        val = data[key]
        if isinstance(val, dict):
            return val
        if isinstance(val, str):
            try:
                return json.loads(val)
            except:
                return {}
        return {}
    nested = data.get("raw_data")
    if isinstance(nested, str):
        try:
            nested_dict = json.loads(nested)
            val = nested_dict.get(key)
            if isinstance(val, dict):
                return val
            if isinstance(val, str):
                try:
                    return json.loads(val)
                except:
                    return {}
        except:
            pass
    return {}

def safe_json_loads(s):
    """安全解析JSON"""
    if s is None:
        return {}
    if isinstance(s, dict):
        return s
    if isinstance(s, str):
        try:
            return json.loads(s)
        except:
            return {}
    return {}

# 导入 rules 模块（不导入 services）
sys.path.insert(0, str(Path(__file__).parent))
from app.rules.rules import infer_r1_with_debug

def load_cases():
    case_file = Path(__file__).parent / "test_system" / "data" / "test_cases.json"
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
        print(f"DEBUG SAMPLE: {sample_id}")
        print("=" * 80)
        print("INPUT TEXT:")
        print(text)
        print("=" * 80)

        # 调用工作流
        extract_data = run_workflow(EXTRACT_WORKFLOW_ID, {"chat_text": text})
        print("\n=== RAW EXTRACT DATA ===")
        print(json.dumps(extract_data, ensure_ascii=False, indent=2))

        s2 = extract_nested_output(extract_data, "S2_output")
        s3 = extract_nested_output(extract_data, "S3_output")

        print("\n=== S2 ===")
        print(json.dumps(s2, ensure_ascii=False, indent=2))
        print("\n=== S3 ===")
        print(json.dumps(s3, ensure_ascii=False, indent=2))

        # 调用规则引擎
        r1_result = infer_r1_with_debug(s2, s3)

        print("\n=== R1 RESULT ===")
        print(json.dumps(r1_result, ensure_ascii=False, indent=2))

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

    # 打印汇总表
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
    for res in all_results:
        sample_id = res["sample_id"]
        expected_stage = None
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