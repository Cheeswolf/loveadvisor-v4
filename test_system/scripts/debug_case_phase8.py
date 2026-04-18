# test_system/scripts/debug_case_phase8.py
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

from app.services.pipeline_service import run_pipeline
from app.services.coze_client import run_workflow
from app.services.result_parser import extract_nested_output
from app.rules.rules import infer_r1_with_debug
from configs.settings import EXTRACT_WORKFLOW_ID, S5_WORKFLOW_ID


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

    for case in matched:
        sample_id = case.get("sample_id", "UNKNOWN")
        text = case.get("input_text", "")

        print("\n" + "=" * 80)
        print(f"DEBUG CASE: {sample_id}")
        print("=" * 80)
        print("INPUT TEXT:")
        print(text)
        print("=" * 80)

        # 首先调用工作流获取 S2 和 S3
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

        # 继续运行完整 pipeline（可选）
        print("\n=== FULL PIPELINE RESULT ===")
        final_result = run_pipeline(text)
        print(json.dumps(final_result, ensure_ascii=False, indent=2))

        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()