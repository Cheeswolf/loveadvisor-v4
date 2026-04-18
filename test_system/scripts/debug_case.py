# test_system/scripts/debug_case.py
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


TARGET_IDS = {"C1", "C3", "E2", "E3"}   # 改成 {"E1"} / {"B3", "E1"} 都可以


def load_cases() -> list:
    case_file = PROJECT_ROOT / "test_system" / "data" / "test_cases.json"
    with open(case_file, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    cases = load_cases()
    matched = [case for case in cases if case.get("sample_id") in TARGET_IDS]

    if not matched:
        print(f"未找到目标样本: {TARGET_IDS}")
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

        result = run_pipeline(text)

        print("\nFINAL RETURN:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()